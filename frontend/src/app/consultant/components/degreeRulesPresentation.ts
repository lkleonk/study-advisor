import type { ProgramRuleSection, ProgramRulesCatalogue } from "@/types/api";

export const RULE_GROUPS = [
  {
    id: "structure",
    label: "Structure & credits",
    hint: "How your degree fits together",
  },
  {
    id: "modules",
    label: "Choosing modules",
    hint: "Options, requirements & limits",
  },
  {
    id: "exams",
    label: "Exams & thesis",
    hint: "Registration, attempts & graduation",
  },
  {
    id: "recognition",
    label: "Recognition & abroad",
    hint: "Earlier credits & special situations",
  },
] as const;

export type RuleGroupId = (typeof RULE_GROUPS)[number]["id"] | "all";

// Presentation only. All requirements and numerical values come from the API.
const STRUCTURE_IDS = new Set([
  "overall-structure",
  "informatics-area",
  "application-area",
  "wahlbereich",
  "informatics-structure",
  "kernfach-structure",
  "synchronisation",
  "scientific-computing",
  "research-phase",
  "grundlagenbereich",
  "abv",
  "study-plan",
]);
const EXAM_IDS = new Set([
  "masterarbeit",
  "bachelorarbeit",
  "examinations",
  "exam-registration",
  "exam-attempts-and-improvement",
  "admission",
]);
const RECOGNITION_IDS = new Set([
  "cross-university-courses",
  "module-rebooking",
  "professional-experience",
  "study-abroad",
  "advising-and-abroad",
  "double-degree",
  "bachelor-modules",
]);

export function ruleGroup(section: ProgramRuleSection): RuleGroupId {
  if (STRUCTURE_IDS.has(section.id)) return "structure";
  if (EXAM_IDS.has(section.id)) return "exams";
  if (RECOGNITION_IDS.has(section.id)) return "recognition";
  // New and degree-specific sections stay discoverable without a frontend update.
  return "modules";
}

export function normalizedRuleText(text: string): string {
  return text
    .normalize("NFKD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase()
    .replace(/ß/g, "ss");
}

export function matchingRules(sections: ProgramRuleSection[], query: string) {
  const words = normalizedRuleText(query).trim().split(/\s+/).filter(Boolean);
  const matches = (text: string) =>
    words.every((word) => normalizedRuleText(text).includes(word));
  return sections.flatMap((section) => {
    const sectionMatches = matches(`${section.title} ${section.description}`);
    const items = sectionMatches
      ? section.items
      : section.items.filter((item) => matches(`${item.label} ${item.text}`));
    const sourceMatches = section.sources.some((source) =>
      matches(`${source.label} ${source.note ?? ""}`),
    );
    return sectionMatches || items.length > 0 || sourceMatches
      ? [{ ...section, items: sourceMatches ? section.items : items }]
      : [];
  });
}

function exactCredits(item: ProgramRuleSection["items"][number]) {
  return (
    item.unit === "LP" && item.minimum !== null && item.minimum === item.maximum
  );
}

export function degreeOverview(catalogue: ProgramRulesCatalogue) {
  const overall = catalogue.sections.find(
    (section) => section.id === "overall-structure",
  );
  const total = overall?.items.find(
    (item) => exactCredits(item) && /total/i.test(item.label),
  );
  const allocationIds = [
    "informatics-area",
    "application-area",
    "wahlbereich",
    "masterarbeit",
  ];
  const allocations = allocationIds.map((id) =>
    catalogue.sections.find((section) => section.id === id),
  );
  const hasSeparateAllocations = allocations.every((section) =>
    section?.items.some(exactCredits),
  );
  const cards = hasSeparateAllocations
    ? allocations.flatMap((section) => {
        if (!section) return [];
        const item = section.items.find(exactCredits)!;
        return [
          {
            label: section.title
              .replace(/^\d+\.\s*/, "")
              .replace(/\s*\(\d+ LP\)$/, ""),
            value: item.minimum!,
            sectionId: section.id,
          },
        ];
      })
    : (overall?.items ?? [])
        .filter((item) => exactCredits(item) && item !== total)
        .map((item) => ({
          label: item.label,
          value: item.minimum!,
          sectionId: overall!.id,
        }));
  return { total: total?.minimum, cards };
}
