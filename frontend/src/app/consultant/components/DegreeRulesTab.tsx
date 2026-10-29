"use client";

import CheckIcon from "@mui/icons-material/Check";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import LaunchOutlinedIcon from "@mui/icons-material/LaunchOutlined";
import SportsEsportsOutlinedIcon from "@mui/icons-material/SportsEsportsOutlined";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Accordion from "@mui/material/Accordion";
import AccordionDetails from "@mui/material/AccordionDetails";
import AccordionSummary from "@mui/material/AccordionSummary";
import Stack from "@mui/material/Stack";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useState } from "react";

import { useDegree } from "@/context/DegreeContext";
import { getProgramRules } from "@/services/api";
import type { ProgramRulesCatalogue } from "@/types/api";

import { buildDegreeRulesText, itemRange } from "./degreeRulesText";
import { LinkifiedText } from "./LinkifiedText";

/** External escape-room game per degree; degrees without an entry show no game banner. */
const ESCAPE_ROOM_URL_BY_DEGREE: Record<string, string> = {
  bsc_informatik: "https://degree-escape-room.vercel.app/",
  msc_informatik: "https://degree-escape-room.vercel.app/",
  msc_data_science: "https://degree-escape-room.vercel.app/",
};

export function DegreeRulesTab() {
  const { effectiveDegreeId } = useDegree();
  const escapeRoomUrl = ESCAPE_ROOM_URL_BY_DEGREE[effectiveDegreeId];
  const [catalogue, setCatalogue] = useState<ProgramRulesCatalogue | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const copyDegreeRules = useCallback(async () => {
    if (!catalogue) return;
    try {
      await navigator.clipboard.writeText(buildDegreeRulesText(catalogue));
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setError("Could not copy to the clipboard.");
    }
  }, [catalogue]);

  const loadRules = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      setCatalogue(await getProgramRules(effectiveDegreeId));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Failed to load degree rules.");
    } finally {
      setIsLoading(false);
    }
  }, [effectiveDegreeId]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadRules();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [loadRules]);

  return (
    <Box sx={{ height: "100%", overflowY: "auto", px: { xs: 1.5, md: 3 }, py: 2 }}>
        <Stack spacing={2} sx={{ maxWidth: 1100, mx: "auto" }}>
        <Box>
          <Stack direction="row" spacing={1} sx={{ alignItems: "center", flexWrap: "wrap" }}>
            <Typography variant="h2">Degree Rules</Typography>
            {catalogue && (
              <Chip label={catalogue.catalogue_version} size="small" variant="outlined" />
            )}
            <Box sx={{ flexGrow: 1 }} />
            <Tooltip title="Copies these degree rules as text. Paste them into another AI assistant (e.g. ChatGPT, Claude or Gemini) to discuss your degree there.">
              <span>
                <Button
                  size="small"
                  startIcon={copied ? <CheckIcon /> : <ContentCopyIcon />}
                  onClick={() => void copyDegreeRules()}
                  disabled={!catalogue}
                >
                  {copied ? "Copied" : "Copy"}
                </Button>
              </span>
            </Tooltip>
          </Stack>
          {catalogue && (
            <Typography variant="body2" sx={{ color: "text.secondary", mt: 0.5 }}>
              {catalogue.degree_program} - {catalogue.regulation}
            </Typography>
          )}
          {catalogue && (
            <Typography variant="caption" sx={{ color: "text.secondary", display: "block", mt: 0.5 }}>
              {catalogue.source_note}
            </Typography>
          )}
        </Box>

          {escapeRoomUrl && (
          <Box
            component="section"
            aria-label="Degree escape room"
            sx={{
              display: "flex",
              flexWrap: "wrap",
              alignItems: "center",
              gap: 1,
              px: 1.5,
              py: 0.75,
              border: 1,
              borderColor: "divider",
              borderRadius: 2,
              bgcolor: "background.paper",
            }}
          >
            <SportsEsportsOutlinedIcon color="primary" fontSize="small" />
            <Typography variant="body2" sx={{ flexGrow: 1, color: "text.secondary" }}>
              Learn the degree through play in Modulio&apos;s external escape room.
            </Typography>
            <Button
              size="small"
              variant="outlined"
              endIcon={<LaunchOutlinedIcon />}
              href={escapeRoomUrl}
              target="_blank"
              rel="noopener noreferrer"
              sx={{ flexShrink: 0 }}
            >
              Play the escape room
            </Button>
          </Box>
          )}

          {isLoading && (
          <Stack direction="row" spacing={1} sx={{ alignItems: "center", color: "text.secondary" }}>
            <CircularProgress size={18} />
            <Typography variant="body2">Loading degree rules</Typography>
          </Stack>
        )}

        {error && <Alert severity="error">{error}</Alert>}

        {catalogue && (
          <Stack spacing={1}>
            {catalogue.sections.map((section) => (
              <Accordion key={`${effectiveDegreeId}-${section.id}`} defaultExpanded={section.id === "overall-structure"} disableGutters variant="outlined">
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box>
                    <Typography variant="h3">{section.title}</Typography>
                    <Typography variant="body2" sx={{ color: "text.secondary", mt: 0.5 }}>
                      {section.description}
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Stack spacing={1.5}>
                    {section.items.map((item) => {
                      const range = itemRange(item);
                      return (
                        <Box
                          key={`${section.id}-${item.label}`}
                          sx={{
                            borderTop: 1,
                            borderColor: "divider",
                            pt: 1.25,
                          }}
                        >
                          <Stack
                            direction={{ xs: "column", sm: "row" }}
                            spacing={1}
                            sx={{
                              alignItems: { xs: "flex-start", sm: "center" },
                              justifyContent: "space-between",
                            }}
                          >
                            <Typography variant="body1" sx={{ fontWeight: 700 }}>
                              {item.label}
                            </Typography>
                            {range && <Chip label={range} size="small" variant="outlined" />}
                          </Stack>
                          <Box sx={{ typography: "body2", color: "text.secondary", mt: 0.5 }}>
                            <LinkifiedText text={item.text} />
                          </Box>
                        </Box>
                      );
                    })}

                    {section.sources.length > 0 && (
                      <Stack direction="row" spacing={0.75} sx={{ flexWrap: "wrap" }}>
                        {section.sources.map((source) => (
                          <Chip
                            key={`${section.id}-${source.label}`}
                            label={source.label}
                            size="small"
                            variant="outlined"
                            {...(source.path.startsWith("http")
                              ? {
                                  component: "a",
                                  href: source.path,
                                  target: "_blank",
                                  rel: "noreferrer",
                                  clickable: true,
                                }
                              : {})}
                          />
                        ))}
                      </Stack>
                    )}

                    {section.related_issue_codes.length > 0 && (
                      <Stack direction="row" spacing={0.75} sx={{ flexWrap: "wrap" }}>
                        {section.related_issue_codes.map((code) => (
                          <Chip key={`${section.id}-${code}`} label={code} size="small" />
                        ))}
                      </Stack>
                    )}
                  </Stack>
                </AccordionDetails>
              </Accordion>
            ))}
          </Stack>
        )}
      </Stack>
    </Box>
  );
}
