"use client";

import CheckIcon from "@mui/icons-material/Check";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import SearchIcon from "@mui/icons-material/Search";
import CloseIcon from "@mui/icons-material/Close";
import LaunchOutlinedIcon from "@mui/icons-material/LaunchOutlined";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Accordion from "@mui/material/Accordion";
import AccordionDetails from "@mui/material/AccordionDetails";
import AccordionSummary from "@mui/material/AccordionSummary";
import IconButton from "@mui/material/IconButton";
import InputAdornment from "@mui/material/InputAdornment";
import Link from "@mui/material/Link";
import MenuItem from "@mui/material/MenuItem";
import Paper from "@mui/material/Paper";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useState } from "react";

import { DEV_TOOLS_ENABLED } from "@/config/publicConfig";
import { useDegree } from "@/context/DegreeContext";
import { getProgramRules } from "@/services/api";
import type { ProgramRuleSection, ProgramRulesCatalogue } from "@/types/api";

import { buildDegreeRulesText, itemRange } from "./degreeRulesText";
import {
  degreeOverview,
  matchingRules,
  RULE_GROUPS,
  ruleGroup,
  type RuleGroupId,
} from "./degreeRulesPresentation";
import { LinkifiedText } from "./LinkifiedText";

const ESCAPE_ROOM_URL_BY_DEGREE: Record<string, string> = {
  bsc_informatik: "https://degree-escape-room.vercel.app/",
  msc_informatik: "https://degree-escape-room.vercel.app/",
  msc_data_science: "https://degree-escape-room.vercel.app/",
};

const VISUALLY_HIDDEN = {
  position: "absolute",
  width: 1,
  height: 1,
  overflow: "hidden",
  clip: "rect(0 0 0 0)",
  whiteSpace: "nowrap",
} as const;

function RuleDetails({ section }: { section: ProgramRuleSection }) {
  return (
    <Stack spacing={2}>
      <Box
        sx={{ typography: "body2", color: "text.secondary", maxWidth: "80ch" }}
      >
        <LinkifiedText text={section.description} />
      </Box>
      {section.items.map((item) => (
        <Box
          key={item.label}
          sx={{ borderTop: 1, borderColor: "divider", pt: 1.5 }}
        >
          <Stack
            direction="row"
            spacing={1}
            sx={{
              alignItems: "baseline",
              justifyContent: "space-between",
              flexWrap: "wrap",
              rowGap: 0.5,
            }}
          >
            <Typography component="h4" variant="body2" sx={{ fontWeight: 700 }}>
              {item.label}
            </Typography>
            {itemRange(item) && (
              <Chip label={itemRange(item)} size="small" variant="outlined" />
            )}
          </Stack>
          <Box
            sx={{
              typography: "body2",
              color: "text.secondary",
              mt: 0.75,
              maxWidth: "80ch",
              lineHeight: 1.65,
            }}
          >
            <LinkifiedText text={item.text} />
          </Box>
        </Box>
      ))}
      {section.sources.length > 0 && (
        <Box sx={{ borderTop: 1, borderColor: "divider", pt: 1.5 }}>
          <Typography variant="overline" sx={{ color: "text.secondary" }}>
            Official references
          </Typography>
          <Stack spacing={0.75}>
            {section.sources.map((source) => (
              <Box
                key={`${source.label}-${source.path}`}
                sx={{ typography: "caption", overflowWrap: "anywhere" }}
              >
                {/^https?:/.test(source.path) ? (
                  <Link
                    href={source.path}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {source.label} ↗
                  </Link>
                ) : (
                  <Typography variant="caption">{source.label}</Typography>
                )}
                {source.note && (
                  <Typography
                    variant="caption"
                    sx={{ display: "block", color: "text.secondary", mt: 0.25 }}
                  >
                    {source.note}
                  </Typography>
                )}
              </Box>
            ))}
          </Stack>
        </Box>
      )}
      {DEV_TOOLS_ENABLED && section.related_issue_codes.length > 0 && (
        <Box
          component="details"
          sx={{ typography: "caption", color: "text.secondary" }}
        >
          <Box component="summary" sx={{ cursor: "pointer" }}>
            Validation references
          </Box>
          <Typography variant="caption" sx={{ overflowWrap: "anywhere" }}>
            {section.related_issue_codes.join(", ")}
          </Typography>
        </Box>
      )}
    </Stack>
  );
}

export function DegreeRulesTab() {
  const { effectiveDegreeId } = useDegree();
  return (
    <DegreeRulesForDegree
      key={effectiveDegreeId}
      degreeId={effectiveDegreeId}
    />
  );
}

function DegreeRulesForDegree({ degreeId }: { degreeId: string }) {
  const [catalogue, setCatalogue] = useState<ProgramRulesCatalogue | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [group, setGroup] = useState<RuleGroupId>("structure");
  const [query, setQuery] = useState("");
  const [expandedIds, setExpandedIds] = useState<string[]>([]);
  const escapeRoomUrl = ESCAPE_ROOM_URL_BY_DEGREE[degreeId];

  const loadRules = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      setCatalogue(await getProgramRules(degreeId));
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : "Failed to load degree rules.",
      );
    } finally {
      setIsLoading(false);
    }
  }, [degreeId]);

  useEffect(() => {
    const timer = window.setTimeout(() => void loadRules(), 0);
    return () => window.clearTimeout(timer);
  }, [loadRules]);

  const copyDegreeRules = async () => {
    if (!catalogue) return;
    try {
      await navigator.clipboard.writeText(buildDegreeRulesText(catalogue));
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setError("Could not copy to the clipboard.");
    }
  };

  const overview = catalogue ? degreeOverview(catalogue) : null;
  const searching = query.trim().length > 0;
  const visibleSections = !catalogue
    ? []
    : searching
      ? matchingRules(catalogue.sections, query)
      : catalogue.sections.filter(
          (section) => group === "all" || ruleGroup(section) === group,
        );
  const allExpanded =
    visibleSections.length > 0 &&
    visibleSections.every((section) => expandedIds.includes(section.id));

  const availableGroups = !catalogue
    ? []
    : RULE_GROUPS.map((entry) => ({
        ...entry,
        count: catalogue.sections.filter(
          (section) => ruleGroup(section) === entry.id,
        ).length,
      })).filter((entry) => entry.count > 0);
  const activeTab =
    !searching && availableGroups.some((entry) => entry.id === group)
      ? group
      : false;
  const selectedTopic =
    activeTab || (!searching && group === "all") ? group : "";

  return (
    <Box
      sx={{ height: "100%", overflowY: "auto", px: { xs: 1.5, md: 3 }, py: 2 }}
    >
      {/* The active tab already names this view; keep a heading for screen readers. */}
      <Typography component="h2" sx={VISUALLY_HIDDEN}>
        Degree Rules
      </Typography>
      <Stack spacing={2.5} sx={{ maxWidth: 1100, mx: "auto", minWidth: 0 }}>
        {isLoading && (
          <Stack
            direction="row"
            spacing={1}
            sx={{ alignItems: "center", color: "text.secondary" }}
          >
            <CircularProgress size={18} />
            <Typography variant="body2">Loading degree rules</Typography>
          </Stack>
        )}
        {error && (
          <Alert
            severity="error"
            action={
              !catalogue ? (
                <Button color="inherit" onClick={() => void loadRules()}>
                  Retry
                </Button>
              ) : undefined
            }
          >
            {error}
          </Alert>
        )}

        {catalogue && overview && (
          <>
            {overview.cards.length > 0 && (
              <Box
                component="section"
                aria-label="Degree at a glance"
                sx={{
                  display: "grid",
                  gridTemplateColumns: {
                    xs: "repeat(2, minmax(0, 1fr))",
                    md: `repeat(${Math.min(overview.cards.length, 4)}, minmax(0, 1fr))`,
                  },
                  gap: 1,
                }}
              >
                {overview.cards.map((card) => (
                  <Box
                    key={card.label}
                    sx={{
                      px: 1.5,
                      py: 1.25,
                      borderRadius: 1,
                      bgcolor: "action.hover",
                    }}
                  >
                    <Typography
                      component="div"
                      sx={{
                        color: "primary.main",
                        fontSize: "1.4rem",
                        lineHeight: 1.2,
                        fontWeight: 700,
                      }}
                    >
                      {card.value}{" "}
                      <Box
                        component="span"
                        sx={{ fontSize: "0.8rem", fontWeight: 400 }}
                      >
                        LP
                      </Box>
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 0.25 }}>
                      {card.label}
                    </Typography>
                  </Box>
                ))}
              </Box>
            )}

            <Box>
              <Tabs
                value={activeTab}
                onChange={(_, value: RuleGroupId) => {
                  setGroup(value);
                  setQuery("");
                }}
                aria-label="Rule topics"
                variant="scrollable"
                scrollButtons={false}
                sx={{
                  display: { xs: "none", md: "flex" },
                  minHeight: 0,
                  "& .MuiTabs-indicator": { display: "none" },
                }}
              >
                {availableGroups.map((entry) => (
                  <Tab
                    key={entry.id}
                    value={entry.id}
                    id={`rules-tab-${entry.id}`}
                    aria-controls="degree-rules-panel"
                    label={
                      <span>
                        {entry.label}{" "}
                        <Box component="span" sx={{ fontWeight: 400 }}>
                          · {entry.count}
                        </Box>
                      </span>
                    }
                    sx={{
                      flex: "1 0 auto",
                      minHeight: 0,
                      px: 2,
                      py: 1.25,
                      textTransform: "none",
                      fontSize: "1rem",
                      color: "text.secondary",
                      border: 1,
                      borderColor: "transparent",
                      borderBottomColor: "divider",
                      borderRadius: "8px 8px 0 0",
                      "&.Mui-selected": {
                        color: "text.primary",
                        fontWeight: 700,
                        bgcolor: "background.paper",
                        borderColor: "divider",
                        borderBottomColor: "background.paper",
                      },
                    }}
                  />
                ))}
              </Tabs>
              <Box
                id="degree-rules-panel"
                role={activeTab ? "tabpanel" : undefined}
                aria-labelledby={
                  activeTab ? `rules-tab-${activeTab}` : undefined
                }
                sx={{
                  border: 1,
                  borderTop: { xs: 1, md: 0 },
                  borderColor: "divider",
                  borderRadius: { xs: "8px", md: "0 0 8px 8px" },
                  bgcolor: "background.paper",
                  p: { xs: 1, md: 1.5 },
                }}
              >
                <TextField
                  select
                  fullWidth
                  size="small"
                  value={selectedTopic}
                  onChange={(event) => {
                    setGroup(event.target.value as RuleGroupId);
                    setQuery("");
                  }}
                  sx={{
                    display: { xs: "flex", md: "none" },
                    mb: 1,
                    "& .MuiSelect-select": {
                      fontSize: "1rem",
                      fontWeight: 700,
                    },
                  }}
                  slotProps={{
                    select: {
                      displayEmpty: true,
                      SelectDisplayProps: { "aria-label": "Rule topic" },
                    },
                  }}
                >
                  <MenuItem value="" sx={{ display: "none" }}>
                    Search results
                  </MenuItem>
                  {availableGroups.map((entry) => (
                    <MenuItem key={entry.id} value={entry.id}>
                      {entry.label} · {entry.count}
                    </MenuItem>
                  ))}
                  <MenuItem value="all">All topics</MenuItem>
                </TextField>
                <Stack
                  direction="row"
                  sx={{
                    alignItems: "center",
                    justifyContent: "space-between",
                    flexWrap: "wrap",
                    gap: 1,
                    mb: 1,
                  }}
                >
                  <TextField
                    size="small"
                    placeholder="Search all rules"
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    sx={{ flex: "1 1 240px", maxWidth: { sm: 360 } }}
                    slotProps={{
                      htmlInput: { "aria-label": "Search all rules" },
                      input: {
                        startAdornment: (
                          <InputAdornment position="start">
                            <SearchIcon fontSize="small" />
                          </InputAdornment>
                        ),
                        endAdornment: query ? (
                          <InputAdornment position="end">
                            <IconButton
                              aria-label="Clear rule search"
                              size="small"
                              onClick={() => setQuery("")}
                            >
                              <CloseIcon fontSize="small" />
                            </IconButton>
                          </InputAdornment>
                        ) : undefined,
                      },
                    }}
                  />
                  <Stack
                    direction="row"
                    sx={{ alignItems: "center", flexWrap: "wrap", gap: 0.5 }}
                  >
                    <Typography
                      component="span"
                      variant="body2"
                      aria-live="polite"
                      sx={{ color: "text.secondary", mr: 0.5 }}
                    >
                      {searching || group === "all"
                        ? `${visibleSections.length} ${
                            visibleSections.length === 1 ? "topic" : "topics"
                          }`
                        : ""}
                    </Typography>
                    {group !== "all" && (
                      <Button
                        size="small"
                        sx={{ display: { xs: "none", md: "inline-flex" } }}
                        onClick={() => {
                          setGroup("all");
                          setQuery("");
                        }}
                      >
                        All topics
                      </Button>
                    )}
                    {!searching && visibleSections.length > 0 && (
                      <Button
                        size="small"
                        onClick={() =>
                          setExpandedIds((ids) =>
                            allExpanded
                              ? ids.filter(
                                  (id) =>
                                    !visibleSections.some(
                                      (section) => section.id === id,
                                    ),
                                )
                              : [
                                  ...new Set([
                                    ...ids,
                                    ...visibleSections.map(
                                      (section) => section.id,
                                    ),
                                  ]),
                                ],
                          )
                        }
                      >
                        {allExpanded ? "Collapse all" : "Expand all"}
                      </Button>
                    )}
                    <Tooltip title="Copies the complete catalogue, including topics hidden by your search or selected group.">
                      <Button
                        size="small"
                        startIcon={copied ? <CheckIcon /> : <ContentCopyIcon />}
                        onClick={() => void copyDegreeRules()}
                      >
                        {copied ? "Copied" : "Copy all rules"}
                      </Button>
                    </Tooltip>
                  </Stack>
                </Stack>
                <Stack spacing={1}>
                  {visibleSections.map((section) => {
                    if (searching)
                      return (
                        <Paper
                          key={section.id}
                          variant="outlined"
                          component="section"
                          aria-label={section.title}
                          sx={{ p: 2 }}
                        >
                          <Typography
                            component="h4"
                            variant="subtitle2"
                            sx={{ mb: 1.5 }}
                          >
                            {section.title}
                          </Typography>
                          <RuleDetails section={section} />
                        </Paper>
                      );
                    const expanded = expandedIds.includes(section.id);
                    return (
                      <Accordion
                        key={section.id}
                        expanded={expanded}
                        onChange={(_, isExpanded) => {
                          setExpandedIds((ids) =>
                            isExpanded
                              ? [...ids, section.id]
                              : ids.filter((id) => id !== section.id),
                          );
                        }}
                        disableGutters
                        variant="outlined"
                        slotProps={{ transition: { unmountOnExit: true } }}
                        sx={{ "&::before": { display: "none" } }}
                      >
                        <AccordionSummary
                          expandIcon={<ExpandMoreIcon />}
                          aria-controls={`rules-${section.id}-content`}
                          id={`rules-${section.id}-heading`}
                        >
                          <Typography
                            component="h4"
                            variant="body2"
                            sx={{ fontWeight: 700, pr: 1 }}
                          >
                            {section.title}
                          </Typography>
                        </AccordionSummary>
                        <AccordionDetails id={`rules-${section.id}-content`}>
                          <RuleDetails section={section} />
                        </AccordionDetails>
                      </Accordion>
                    );
                  })}
                  {visibleSections.length === 0 && (
                    <Paper
                      variant="outlined"
                      sx={{ p: 3, textAlign: "center" }}
                    >
                      <Typography variant="body2">
                        No rules match “{query}”. Try another term or browse the
                        topics.
                      </Typography>
                      <Button size="small" onClick={() => setQuery("")}>
                        Clear search
                      </Button>
                    </Paper>
                  )}
                </Stack>
              </Box>
            </Box>

            <Box sx={{ borderTop: 1, borderColor: "divider", pt: 1.5 }}>
              <Typography variant="caption" sx={{ color: "text.secondary" }}>
                Use this guide for orientation. Official regulations and the
                examination office remain authoritative.
              </Typography>
              <Accordion
                disableGutters
                elevation={0}
                sx={{
                  mt: 0.75,
                  bgcolor: "transparent",
                  "&::before": { display: "none" },
                }}
              >
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="body2">
                    Regulation & source details
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Stack spacing={1}>
                    <Typography variant="body2">
                      {catalogue.regulation}
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{ color: "text.secondary" }}
                    >
                      {catalogue.source_note}
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{ color: "text.secondary" }}
                    >
                      Catalogue: {catalogue.catalogue_version}
                    </Typography>
                  </Stack>
                </AccordionDetails>
              </Accordion>
              {escapeRoomUrl && (
                <Button
                  size="small"
                  href={escapeRoomUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  endIcon={<LaunchOutlinedIcon />}
                  sx={{ mt: 0.5 }}
                >
                  Explore the degree in the escape room
                </Button>
              )}
            </Box>
          </>
        )}
      </Stack>
    </Box>
  );
}
