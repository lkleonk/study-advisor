import type { ProgramRuleItem, ProgramRulesCatalogue } from "@/types/api";

import { buildConversationText } from "./chatExport";
import type { ChatMessage } from "./chatMessages";

export function itemRange(item: ProgramRuleItem) {
  if (item.minimum !== null && item.maximum !== null && item.minimum === item.maximum) {
    return `${item.minimum} ${item.unit ?? ""}`.trim();
  }
  if (item.minimum !== null && item.maximum !== null) {
    return `${item.minimum}-${item.maximum} ${item.unit ?? ""}`.trim();
  }
  if (item.minimum !== null) {
    return `min ${item.minimum} ${item.unit ?? ""}`.trim();
  }
  if (item.maximum !== null) {
    return `max ${item.maximum} ${item.unit ?? ""}`.trim();
  }
  return null;
}

/**
 * Plain-text degree rules for pasting into another AI assistant. The two
 * framing lines keep that assistant to the rules; Modulio's own backend prompts
 * are never included. An optional conversation is appended so users can
 * continue where they left off.
 */
export function buildDegreeRulesText(
  catalogue: ProgramRulesCatalogue,
  conversation: ChatMessage[] = [],
) {
  const lines = [
    `You are a study advisor for the ${catalogue.degree_program} at Freie Universität Berlin.`,
    "Answer questions about the degree using only the rules below. If something is not covered, say so and refer to the official regulation or the examination office instead of guessing. Do not invent module names, credit points or deadlines.",
    "",
    `# ${catalogue.degree_program} - ${catalogue.regulation}`,
    catalogue.source_note,
  ];
  for (const section of catalogue.sections) {
    lines.push("", `## ${section.title}`, section.description);
    for (const item of section.items) {
      const range = itemRange(item);
      lines.push(`- ${item.label}${range ? ` (${range})` : ""}: ${item.text}`);
    }
    for (const source of section.sources) {
      if (source.path.startsWith("http")) {
        lines.push(`- Official source: ${source.label} (${source.path})`);
      }
    }
  }
  if (conversation.length > 0) {
    lines.push(
      "",
      "# Conversation so far",
      "The student already discussed the following with another study advisor. Continue from here.",
      "",
      buildConversationText(conversation),
    );
  }
  return lines.join("\n");
}
