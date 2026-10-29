export type MessageType = "degree_question" | "course_offering_question" | "plan_check" | "off_topic";

export type Citation = {
  source: string;
  title: string | null;
  section_heading: string | null;
  page: number | null;
  score: number | null;
};

export type RuleIssue = {
  code: string;
  severity: "error" | "warning";
  message: string;
  details: Record<string, unknown>;
};

export type RuleCheckResult = {
  is_valid: boolean;
  summary: string;
  totals: Record<string, number>;
  issues: RuleIssue[];
};

export type ModuleArea =
  | "practical"
  | "theoretical"
  | "technical"
  | "application"
  | "thesis"
  | "unknown";

export type SpecializationArea = "practical" | "theoretical" | "technical";

export type PlannedModule = {
  name: string;
  lp: number;
  area: ModuleArea;
  is_wahlbereich: boolean;
  is_ungraded: boolean;
  is_bachelor_module: boolean;
  is_scientific_work: boolean;
  is_software_project: boolean;
};

export type StudyPlan = {
  specialization_area: SpecializationArea | null;
  modules: PlannedModule[];
};

export type ModelReply = {
  reply: string;
  message_type: MessageType;
  citations: Citation[];
  rule_check_result: RuleCheckResult | null;
  parsed_study_plan: StudyPlan | null;
};

export type TranscriptUploadResponse = {
  filename: string;
  message_type: "plan_check";
  reply: string;
  parsed_study_plan: StudyPlan | null;
  rule_check_result: RuleCheckResult | null;
};

export type ApiErrorDetail = {
  error_code?: string;
  message?: string;
  limit?: number;
  remaining?: number;
  reset_at?: string;
  readability?: Record<string, unknown>;
};

export type UsageQuota = {
  limit: number;
  used: number;
  remaining: number;
  reset_at: string;
};

/** Service-wide allowance, in the same user-action unit as UsageQuota. */
export type ServiceQuota = {
  limit: number;
  used: number;
  remaining: number;
};

export type UsageResponse = UsageQuota & {
  service: ServiceQuota;
  session_inactivity_ttl_seconds: number;
  diagnostic_tracing_enabled: boolean;
  quota_scope: "client_ip";
};

export type QuotaAwareResponse<T> = {
  data: T;
  usage: UsageQuota | null;
};

export type SessionResponse = {
  session_id: string;
  degree: string;
};

export type DegreeInfo = {
  id: string;
  display_name: string;
  regulation: string;
  /** Only degrees with trusted deterministic validation get the Study Plan tab. */
  plan_validation_enabled: boolean;
};

export type HealthResponse = {
  status: "healthy" | "degraded";
  services: Record<string, string>;
};

export type TracingReinitResponse = {
  trace_path: string;
};

export type ProgramRuleSource = {
  label: string;
  path: string;
  note: string | null;
};

export type ProgramRuleItem = {
  label: string;
  text: string;
  minimum: number | null;
  maximum: number | null;
  unit: string | null;
};

export type ProgramRuleSection = {
  id: string;
  title: string;
  description: string;
  items: ProgramRuleItem[];
  related_issue_codes: string[];
  sources: ProgramRuleSource[];
};

export type ProgramRulesCatalogue = {
  degree_program: string;
  regulation: string;
  catalogue_version: string;
  source_note: string;
  sections: ProgramRuleSection[];
};

export type FirstSession = {
  /** ISO date, YYYY-MM-DD. */
  date: string;
  /** HH:MM; start and end are both set or both absent. */
  start?: string | null;
  end?: string | null;
  room?: string | null;
};

export type CourseOfferingItem = {
  title: string;
  module_catalog_name?: string | null;
  /** Official FU module code of the credited module, e.g. "0086eA1.14". */
  fu_module_code?: string | null;
  lp: number | null;
  /** First appointment of each weekly lecture/seminar slot (at most two); not the timetable. */
  first_sessions?: FirstSession[];
  /** First appointment of each Übung group (lectures only); empty while the VV lists none. */
  uebungen?: FirstSession[];
  /** VV page of the lecture's Übung event. */
  uebung_url?: string | null;
  /** Degree-specific crediting caveat for chat context; not shown on cards. */
  credit_note?: string | null;
  url?: string | null;
  is_bachelor_module?: boolean | null;
};

export type CourseOfferingType = {
  id: string;
  label: string;
  courses: CourseOfferingItem[];
};

export type CourseOfferingArea = {
  id: string;
  label: string;
  /** Optional note shown once under the area heading. */
  note?: string | null;
  course_types: CourseOfferingType[];
};

export type CourseOfferingSemester = {
  id: string;
  label: string;
  areas: CourseOfferingArea[];
};

export type CourseOfferingsCatalogue = {
  degree_program: string;
  regulation: string;
  source_note: string;
  semesters: CourseOfferingSemester[];
};
