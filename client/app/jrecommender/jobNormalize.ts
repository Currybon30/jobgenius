export type JobCardData = {
  id: string;
  title: string;
  company: string;
  logo?: string | null;
  location: string;
  remote: boolean;
  employmentType?: string | null;
  salary?: string | null;
  applyLink?: string | null;
  description?: string | null;
  matchScore?: number | null;
  skills: string[];
};

export type JobsPayload = {
  jobs: JobCardData[];
  message?: string;
  provider?: string;
};

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
}

function asString(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

function asStringList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value
    .filter((item): item is string => typeof item === "string" && item.trim().length > 0)
    .map((item) => item.trim())
    .slice(0, 6);
}

function formatSalary(salary: Record<string, unknown>, raw: Record<string, unknown>): string | null {
  const direct =
    asString(salary.job_salary_string) ||
    asString(raw.job_salary) ||
    asString(raw.job_salary_string);
  if (direct) return direct;

  const min = salary.job_salary_min ?? raw.job_min_salary;
  const max = salary.job_salary_max ?? raw.job_max_salary;
  const currency = asString(salary.job_salary_currency) || "CAD";
  const minN = typeof min === "number" ? min : Number(min);
  const maxN = typeof max === "number" ? max : Number(max);
  if (Number.isFinite(minN) && Number.isFinite(maxN)) {
    return `${currency} ${Math.round(minN).toLocaleString()} – ${Math.round(maxN).toLocaleString()}`;
  }
  if (Number.isFinite(minN)) return `From ${currency} ${Math.round(minN).toLocaleString()}`;
  if (Number.isFinite(maxN)) return `Up to ${currency} ${Math.round(maxN).toLocaleString()}`;
  return null;
}

function excerpt(text: string, max = 180): string {
  if (text.length <= max) return text;
  return `${text.slice(0, max).trimEnd()}…`;
}

export function normalizeJob(raw: unknown, index: number): JobCardData | null {
  if (!raw || typeof raw !== "object") return null;

  const item = raw as Record<string, unknown>;
  const wrapped =
    item.job && typeof item.job === "object" && !Array.isArray(item.job)
      ? (item.job as Record<string, unknown>)
      : item;

  const companyObj = asRecord(wrapped.company);
  const locationObj = asRecord(wrapped.location);
  const salaryObj = asRecord(wrapped.salary);

  const title = asString(wrapped.title) || asString(wrapped.job_title) || "Untitled role";
  const company =
    asString(companyObj.employer_name) ||
    asString(wrapped.employer_name) ||
    "Company";
  const logo =
    asString(companyObj.employer_logo) ||
    asString(wrapped.employer_logo) ||
    null;

  const city = asString(locationObj.city) || asString(wrapped.job_city);
  const province = asString(locationObj.province) || asString(wrapped.job_state);
  const country = asString(locationObj.country) || asString(wrapped.job_country);
  const remote = Boolean(locationObj.remote ?? wrapped.job_is_remote);
  const locationParts = [city, province, country].filter(Boolean);
  const location =
    locationParts.join(", ") || (remote ? "Remote" : "Location TBD");

  const employmentType =
    asString(wrapped.employment_type) ||
    asString(wrapped.job_employment_type) ||
    null;

  const applyLink =
    asString(wrapped.apply_link) ||
    asString(wrapped.job_apply_link) ||
    null;

  const descriptionRaw =
    asString(wrapped.job_description) || asString(wrapped.description);
  const description = descriptionRaw ? excerpt(descriptionRaw) : null;

  const skills = asStringList(wrapped.skills).length
    ? asStringList(wrapped.skills)
    : asStringList(wrapped.job_required_skills);

  const matchScore =
    typeof item.match_score === "number"
      ? item.match_score
      : typeof wrapped.match_score === "number"
        ? wrapped.match_score
        : null;

  const id =
    asString(wrapped.id) ||
    asString(wrapped.job_id) ||
    `${company}-${title}-${index}`;

  return {
    id,
    title,
    company,
    logo,
    location,
    remote,
    employmentType,
    salary: formatSalary(salaryObj, wrapped),
    applyLink,
    description,
    matchScore,
    skills,
  };
}

export function extractJobsPayload(data: unknown): JobsPayload {
  const record = asRecord(data);
  const list = Array.isArray(record.jobs)
    ? record.jobs
    : Array.isArray(data)
      ? data
      : [];

  const jobs = list
    .map((job, index) => normalizeJob(job, index))
    .filter((job): job is JobCardData => Boolean(job));

  return {
    jobs,
    message: asString(record.message) || undefined,
    provider: asString(record.provider) || undefined,
  };
}
