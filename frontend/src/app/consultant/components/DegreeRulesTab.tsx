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
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import Accordion from "@mui/material/Accordion";
import AccordionDetails from "@mui/material/AccordionDetails";
import AccordionSummary from "@mui/material/AccordionSummary";
import IconButton from "@mui/material/IconButton";
import InputAdornment from "@mui/material/InputAdornment";
import Link from "@mui/material/Link";
import Paper from "@mui/material/Paper";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useTheme } from "@mui/material/styles";
import useMediaQuery from "@mui/material/useMediaQuery";
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
  // Strings on purpose: in MUI sx a bare 1 means 100%, which overflowed the page.
  width: "1px",
  height: "1px",
  m: "-1px",
  p: 0,
  border: 0,
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
  const [copyDialogOpen, setCopyDialogOpen] = useState(false);
  const [copyError, setCopyError] = useState<string | null>(null);
  const [group, setGroup] = useState<RuleGroupId>("structure");
  const [query, setQuery] = useState("");
  const [expandedIds, setExpandedIds] = useState<string[]>([]);
  const isDesktop = useMediaQuery(useTheme().breakpoints.up("md"), {
    noSsr: true,
  });
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

  const openCopyDialog = () => {
    setCopied(false);
    setCopyError(null);
    setCopyDialogOpen(true);
  };

  const copyDegreeRules = async () => {
    if (!catalogue) return;
    setCopyError(null);
    try {
      await navigator.clipboard.writeText(buildDegreeRulesText(catalogue));
      setCopied(true);
    } catch {
      setCopyError(
        "Could not copy to the clipboard. Your browser may block it here.",
      );
    }
  };

  const overview = catalogue ? degreeOverview(catalogue) : null;
  const searching = query.trim().length > 0;
  // Small screens have no topic tabs: they always list every topic, grouped.
  const shownGroup: RuleGroupId = isDesktop ? group : "all";
  const visibleSections = !catalogue
    ? []
    : searching
      ? matchingRules(catalogue.sections, query)
      : catalogue.sections.filter(
          (section) => shownGroup === "all" || ruleGroup(section) === shownGroup,
        );
  const allExpanded =
    visibleSections.length > 0 &&
    visibleSections.every((section) => expandedIds.includes(section.id));

  const availableGroups = !catalogue
    ? []
    : RULE_GROUPS.filter((entry) =>
        catalogue.sections.some((section) => ruleGroup(section) === entry.id),
      );
  const activeTab =
    !searching && availableGroups.some((entry) => entry.id === group)
      ? group
      : false;
  const sectionGroups =
    !searching && shownGroup === "all"
      ? availableGroups
          .map((entry) => ({
            ...entry,
            sections: visibleSections.filter(
              (section) => ruleGroup(section) === entry.id,
            ),
          }))
          .filter((entry) => entry.sections.length > 0)
      : null;

  const renderSection = (section: ProgramRuleSection) => {
    if (searching)
      return (
        <Paper
          key={section.id}
          variant="outlined"
          component="section"
          aria-label={section.title}
          sx={{ p: 2 }}
        >
          <Typography component="h4" variant="subtitle2" sx={{ mb: 1.5 }}>
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
  };

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
              <Stack
                direction="row"
                sx={{ alignItems: "center", flexWrap: "wrap", gap: 1 }}
              >
                <TextField
                  size="small"
                  placeholder="Search all rules"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  sx={{ flex: { xs: "1 1 100%", md: "0 1 360px" } }}
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
                  sx={{
                    alignItems: "center",
                    justifyContent: "space-between",
                    gap: 0.5,
                    flex: { xs: "1 1 100%", md: "0 0 auto" },
                    ml: { md: "auto" },
                  }}
                >
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
                  <Button
                    size="small"
                    startIcon={<ContentCopyIcon />}
                    onClick={openCopyDialog}
                    sx={{ order: { xs: -1, md: 0 } }}
                  >
                    Copy rules
                  </Button>
                </Stack>
              </Stack>
              <Typography
                variant="body2"
                aria-live="polite"
                sx={{
                  color: "text.secondary",
                  mt: 0.75,
                  "&:empty": { display: "none" },
                }}
              >
                {searching
                  ? `${visibleSections.length} ${
                      visibleSections.length === 1 ? "topic" : "topics"
                    }`
                  : ""}
              </Typography>
            </Box>

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
                    label={entry.label}
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
                // Frame only on desktop, where it joins the selected tab.
                sx={{
                  border: { xs: 0, md: 1 },
                  borderTop: 0,
                  borderColor: "divider",
                  borderRadius: { md: "0 0 8px 8px" },
                  bgcolor: { md: "background.paper" },
                  p: { xs: 0, md: 1.5 },
                }}
              >
                <Stack spacing={1}>
                  {sectionGroups
                    ? sectionGroups.map((entry, index) => (
                        <Box
                          key={entry.id}
                          component="section"
                          aria-labelledby={`rules-group-${entry.id}`}
                        >
                          <Typography
                            id={`rules-group-${entry.id}`}
                            component="h3"
                            variant="subtitle2"
                            sx={{
                              color: "text.secondary",
                              fontWeight: 700,
                              mt: index ? 3.5 : 0.5,
                              mb: 1,
                              pb: 0.5,
                              borderBottom: 1,
                              borderColor: "divider",
                            }}
                          >
                            {entry.label}
                          </Typography>
                          <Stack spacing={1}>
                            {entry.sections.map(renderSection)}
                          </Stack>
                        </Box>
                      ))
                    : visibleSections.map(renderSection)}
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
            <Dialog
              open={copyDialogOpen}
              onClose={() => setCopyDialogOpen(false)}
              aria-labelledby="copy-rules-title"
            >
              <DialogTitle id="copy-rules-title">
                Ask another AI about your degree
              </DialogTitle>
              <DialogContent>
                <DialogContentText>
                  Copy the rules for {catalogue.degree_program} and paste them
                  into ChatGPT, Claude or Gemini to keep asking there.
                </DialogContentText>
                <DialogContentText variant="body2" sx={{ mt: 1.5 }}>
                  The copy includes every topic, even ones hidden by your search
                  or selected topic. Official regulations and the examination
                  office remain authoritative.
                </DialogContentText>
                {copied && (
                  <Alert severity="success" sx={{ mt: 2 }}>
                    Copied. Paste it into your AI chat.
                  </Alert>
                )}
                {copyError && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {copyError}
                  </Alert>
                )}
              </DialogContent>
              <DialogActions>
                <Button onClick={() => setCopyDialogOpen(false)}>Close</Button>
                <Button
                  variant="contained"
                  startIcon={copied ? <CheckIcon /> : <ContentCopyIcon />}
                  onClick={() => void copyDegreeRules()}
                >
                  {copied ? "Copied" : "Copy rules"}
                </Button>
              </DialogActions>
            </Dialog>
          </>
        )}
      </Stack>
    </Box>
  );
}
