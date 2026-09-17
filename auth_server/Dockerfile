# Builder stage
FROM eclipse-temurin:17-jdk-alpine AS builder
LABEL org.opencontainers.image.authors="Tuong Nguyen Pham <tuongnguyen2004danang@gmail.com>"
WORKDIR /app

COPY mvnw .
COPY .mvn .mvn
COPY pom.xml .

# make wrapper executable
RUN chmod +x mvnw
RUN ./mvnw dependency:go-offline

COPY src ./src
RUN ./mvnw clean package -DskipTests

# Runtime stage
FROM eclipse-temurin:17-jdk-alpine
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 5000
CMD ["java", "-jar", "app.jar"]