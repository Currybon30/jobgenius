package com.job_recommender_system.auth_server.services;

import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;

import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.job_recommender_system.auth_server.dto.StripePaymentRequest;
import com.job_recommender_system.auth_server.models.Payment;
import com.job_recommender_system.auth_server.models.PaymentMetadata;
import com.job_recommender_system.auth_server.models.User;
import com.job_recommender_system.auth_server.repositories.PaymentMetadataRepository;
import com.job_recommender_system.auth_server.repositories.PaymentRepository;
import com.job_recommender_system.auth_server.repositories.UserRepository;
import com.job_recommender_system.auth_server.utils.FastAPIUpdates;
import com.job_recommender_system.auth_server.utils.PaymentStatus;
import com.stripe.exception.EventDataObjectDeserializationException;
import com.stripe.exception.SignatureVerificationException;
import com.stripe.model.Event;
import com.stripe.model.EventDataObjectDeserializer;
import com.stripe.model.Invoice;
import com.stripe.model.Subscription;
import com.stripe.model.checkout.Session;
import com.stripe.net.Webhook;
import com.stripe.param.checkout.SessionCreateParams;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class StripePaymentService extends PaymentService {
    /*
     * @Value("${STRIPE_WEBHOOK_SECRET_KEY}")
     * private String endpointSecret;
     */
    private final PaymentRepository paymentRepository;
    private final PaymentMetadataRepository paymentMetadataRepository;
    private final UserRepository userRepository;
    private final FastAPIUpdates fastAPIUpdates;

    @Override
    public String createPayment(Object request, Authentication authentication) throws Exception {
        StripePaymentRequest req = (StripePaymentRequest) request;

        User user = userRepository.findByEmail(authentication.getName())
                .orElseThrow(() -> new Exception("User not found"));

        Payment payment = new Payment();
        payment.setStatus(PaymentStatus.PENDING);
        payment.setProvider("STRIPE");
        payment.setAmount(0L); // Will be updated after checkout session is created
        payment.setCurrency("cad"); // Will be updated after checkout session is created
        payment.setProviderPaymentRef(""); // Will be updated after checkout session is created
        payment.setCreatedAt(OffsetDateTime.now(ZoneOffset.UTC));
        payment.setUpdatedAt(OffsetDateTime.now(ZoneOffset.UTC));
        payment.setUser(user);

        payment = paymentRepository.save(payment);

        SessionCreateParams params = SessionCreateParams.builder()
                .setMode(SessionCreateParams.Mode.SUBSCRIPTION)
                .setSuccessUrl(req.getSuccessUrl())
                .setCancelUrl(req.getCancelUrl())
                .setCustomerEmail(user.getEmail())
                .setSubscriptionData(
                        SessionCreateParams.SubscriptionData.builder()
                                .setTrialPeriodDays(14L)
                                .build())
                .putMetadata("userId", user.getUid().toString())
                .addLineItem(
                        SessionCreateParams.LineItem.builder()
                                .setQuantity(1L)
                                .setPrice("price_1TN2z21euurRhDPhjypYOpec")
                                .build())
                .build();

        Session session = Session.create(params);
        payment.setAmount(session.getAmountTotal());
        payment.setCurrency(session.getCurrency());
        payment.setProviderPaymentRef(session.getId());
        paymentRepository.save(payment);

        PaymentMetadata paymentMetadata = new PaymentMetadata();
        paymentMetadata.setPayment(payment);
        paymentMetadata.setKey(""); // Will be updated after checkout session is created
        paymentMetadata.setValue(""); // Will be updated after checkout session is created
        paymentMetadataRepository.save(paymentMetadata);

        return session.getUrl();
    }

    @Override
    public String cancelSubscription(String subscriptionId) throws Exception {
        try {
            Subscription subscription = Subscription.retrieve(subscriptionId);
            Map<String, Object> params = new HashMap<>();
            params.put("cancel_at_period_end", true);

            subscription.update(params);
            return "Subscription cancelled successfully";
        } catch (Exception e) {
            throw new Exception("Failed to cancel subscription: " + e.getMessage());
        }
    }

    @Override
    public void handleWebhook(String payload, String sigHeader)
            throws JsonProcessingException, EventDataObjectDeserializationException {

        String endpointSecret = "whsec_a2efe90df2c747b523120156460089cc171fe04c086586e387848cf1e9523a04"; // move this
                                                                                                          // to
                                                                                                          // application
                                                                                                          // properties
                                                                                                          // or
                                                                                                          // environment
                                                                                                          // variable in
                                                                                                          // production

        Event event;
        try {
            event = Webhook.constructEvent(payload, sigHeader, endpointSecret);
        } catch (SignatureVerificationException e) {
            throw new RuntimeException(e);
        }

        switch (event.getType()) {
            /**
             * 🔥 1. Checkout completed (FIRST TIME subscription)
             */
            case "checkout.session.completed": {
                EventDataObjectDeserializer deserializer = event.getDataObjectDeserializer();

                Session session;
                if (deserializer.getObject().isPresent()) {
                    session = (Session) deserializer.getObject().get();
                } else {

                    session = (Session) deserializer.deserializeUnsafe();
                }
                System.out.println("Received checkout.session.completed event for session: " + session.getId());
                if (session != null) {
                    String paymentRef = session.getId();
                    Payment payment = paymentRepository.findByProviderPaymentRef(paymentRef)
                            .orElseThrow(() -> new RuntimeException("Payment not found"));

                    payment.setStatus(PaymentStatus.PAID);
                    payment.setUpdatedAt(OffsetDateTime.now(ZoneOffset.UTC));
                    paymentRepository.save(payment);

                    PaymentMetadata paymentMetadata = paymentMetadataRepository
                            .findByPayment_PaymentId(payment.getPaymentId())
                            .orElseThrow(() -> new RuntimeException("Payment metadata not found"));
                    paymentMetadata.setKey("Stripe_SubscriptionId");
                    paymentMetadata.setValue(session.getSubscription());
                    paymentMetadataRepository.save(paymentMetadata);

                    User user = payment.getUser();
                    Long uid = user.getUid();
                    String planExpiry = OffsetDateTime.now(ZoneOffset.UTC)
                            .plusDays(14) // Trial period of 14 days for first time subscription, after that it will be
                                          // automatically renewed and charged by Stripe every month
                            .format(DateTimeFormatter.ISO_OFFSET_DATE_TIME);
                    fastAPIUpdates.updatePlanFastAPI(uid.toString(), "PREMIUM", planExpiry);
                }
                break;
            }
            /**
             * 🔁 2. Recurring payment success (monthly renew)
             */
            case "invoice.paid": {
                EventDataObjectDeserializer deserializer = event.getDataObjectDeserializer();

                Invoice invoice;
                if (deserializer.getObject().isPresent()) {
                    invoice = (Invoice) deserializer.getObject().get();
                } else {

                    invoice = (Invoice) deserializer.deserializeUnsafe();
                }

                if (invoice == null)
                    return;

                String subId = invoice.getSubscription();

                PaymentMetadata paymentMetadata = paymentMetadataRepository.findByKeyAndValue("Stripe_SubscriptionId",
                        subId);
                if (paymentMetadata == null)
                    return;
                Payment payment = paymentMetadata.getPayment();

                if (payment != null) {
                    payment.setStatus(PaymentStatus.PAID);
                    payment.setUpdatedAt(OffsetDateTime.now(ZoneOffset.UTC));
                    paymentRepository.save(payment);

                    User user = payment.getUser();
                    Long uid = user.getUid();
                    String planExpiry = OffsetDateTime.now(ZoneOffset.UTC)
                            .plusDays(30)
                            .format(DateTimeFormatter.ISO_OFFSET_DATE_TIME);
                    fastAPIUpdates.updatePlanFastAPI(uid.toString(), "PREMIUM", planExpiry);
                }
                break;
            }

            /**
             * ❌ 3. Recurring payment failed (card expired, insufficient fund, etc)
             * Recharge will be automatically retried by Stripe, but we should mark the
             * payment as failed and update user plan to FREE immediately
             */
            case "invoice.payment_failed": {
                EventDataObjectDeserializer deserializer = event.getDataObjectDeserializer();

                Invoice failedInvoice;

                if (deserializer.getObject().isPresent()) {
                    failedInvoice = (Invoice) deserializer.getObject().get();
                } else {

                    failedInvoice = (Invoice) deserializer.deserializeUnsafe();
                }

                if (failedInvoice == null)
                    return;

                String failedSubId = failedInvoice.getSubscription();

                PaymentMetadata failedPaymentMetadata = paymentMetadataRepository
                        .findByKeyAndValue("Stripe_SubscriptionId", failedSubId);
                if (failedPaymentMetadata == null)
                    return;
                Payment failedPayment = failedPaymentMetadata.getPayment();

                if (failedPayment != null) {
                    failedPayment.setStatus(PaymentStatus.FAILED);
                    failedPayment.setUpdatedAt(OffsetDateTime.now(ZoneOffset.UTC));
                    paymentRepository.save(failedPayment);

                    User user = failedPayment.getUser();
                    Long uid = user.getUid();
                    fastAPIUpdates.updatePlanFastAPI(uid.toString(), "FREE", "");
                }
                break;
            }

            /**
             * 4. Subscription updated (cancel at period end, resume, etc.)
             */
            case "customer.subscription.updated": {
                EventDataObjectDeserializer deserializer = event.getDataObjectDeserializer();

                Subscription updatedSub;

                if (deserializer.getObject().isPresent()) {
                    updatedSub = (Subscription) deserializer.getObject().get();
                } else {

                    updatedSub = (Subscription) deserializer.deserializeUnsafe();
                }

                if (updatedSub == null)
                    return;

                String updatedSubId = updatedSub.getId();

                PaymentMetadata updatedPaymentMetadata = paymentMetadataRepository
                        .findByKeyAndValue("Stripe_SubscriptionId", updatedSubId);
                if (updatedPaymentMetadata == null)
                    return;
                Payment updatedPayment = updatedPaymentMetadata.getPayment();
                if (updatedPayment != null) {
                    if (Boolean.TRUE.equals(updatedSub.getCancelAtPeriodEnd())) {
                        updatedPayment.setStatus(PaymentStatus.CANCELLED);
                        User user = updatedPayment.getUser();
                        Long uid = user.getUid();
                        fastAPIUpdates.updatePlanFastAPI(uid.toString(), "FREE", "");
                    } else {
                        updatedPayment.setStatus(PaymentStatus.PAID);

                        User user = updatedPayment.getUser();
                        Long uid = user.getUid();
                        String planExpiry = OffsetDateTime.now(ZoneOffset.UTC)
                                .plusDays(30)
                                .format(DateTimeFormatter.ISO_OFFSET_DATE_TIME);
                        fastAPIUpdates.updatePlanFastAPI(uid.toString(), "PREMIUM", planExpiry);
                    }
                    updatedPayment.setUpdatedAt(OffsetDateTime.now(ZoneOffset.UTC));
                    paymentRepository.save(updatedPayment);
                }
                break;
            }

            /**
             * 🚫 5. Subscription fully canceled
             */
            case "customer.subscription.deleted": {
                EventDataObjectDeserializer deserializer = event.getDataObjectDeserializer();
                Subscription deletedSub;
                if (deserializer.getObject().isPresent()) {
                    deletedSub = (Subscription) deserializer.getObject().get();
                } else {

                    deletedSub = (Subscription) deserializer.deserializeUnsafe();
                }

                if (deletedSub == null)
                    return;

                String deletedSubId = deletedSub.getId();

                PaymentMetadata deletedPaymentMetadata = paymentMetadataRepository
                        .findByKeyAndValue("Stripe_SubscriptionId", deletedSubId);
                if (deletedPaymentMetadata == null)
                    return;
                Payment deletedPayment = deletedPaymentMetadata.getPayment();
                if (deletedPayment != null) {
                    deletedPayment.setStatus(PaymentStatus.CANCELLED);
                    deletedPayment.setUpdatedAt(OffsetDateTime.now(ZoneOffset.UTC));
                    paymentRepository.save(deletedPayment);
                    User user = deletedPayment.getUser();
                    Long uid = user.getUid();
                    fastAPIUpdates.updatePlanFastAPI(uid.toString(), "FREE", "");
                }
                break;
            }

            default: {
                // Ignore other events
                break;
            }
        }
    }
}
