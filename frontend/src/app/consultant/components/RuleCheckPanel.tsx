import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutlined";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutlined";
import WarningAmberOutlinedIcon from "@mui/icons-material/WarningAmberOutlined";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Divider from "@mui/material/Divider";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import { colors } from "@/theme/colors";
import type { RuleCheckResult, RuleIssue } from "@/types/api";

type RuleCheckPanelProps = {
  result: RuleCheckResult;
  compact?: boolean;
};

/**
 * Blocking rule issues are shown in orange rather than the theme's `error` red,
 * which stays reserved for application failures (failed uploads, chat errors).
 */
export const issueChipSx = {
  bgcolor: colors.issue,
  color: "#ffffff",
} as const;

export const ISSUE_CHIP_MARKER = { "data-rule-issue-chip": "true" } as const;

function formatKey(key: string) {
  const labels: Record<string, string> = {
    informatics_lp: "Informatik (excluding Wahlbereich)",
    application_lp: "Anwendungsbereich (excluding Wahlbereich)",
    wahlbereich_lp: "Wahlbereich",
    module_area_lp: "Taught modules",
    master_total_lp: "Degree total (including planned thesis)",
    total_scientific_work_count: "Seminars (whole plan)",
    total_software_project_count: "Softwareprojekte (whole plan)",
    core_scientific_work_count: "Seminars in Informatik",
    core_software_project_count: "Softwareprojekte in Informatik",
  };
  if (labels[key]) return labels[key];
  return key.replace(/_/g, " ");
}

function issueIcon(issue: RuleIssue) {
  return issue.severity === "error" ? (
    <ErrorOutlineIcon fontSize="small" sx={{ color: colors.issue }} />
  ) : (
    <WarningAmberOutlinedIcon color="warning" fontSize="small" />
  );
}

export function RuleCheckPanel({ result, compact = false }: RuleCheckPanelProps) {
  const issues = result.issues.filter((issue) => issue.severity === "error").length;
  const warnings = result.issues.filter((issue) => issue.severity === "warning").length;
  const totals = Object.entries(result.totals);

  return (
    <Paper
      variant="outlined"
      sx={{
        p: compact ? 1.5 : 2,
        bgcolor: "background.paper",
      }}
    >
      <Stack spacing={1.5}>
        <Stack
          direction={{ xs: "column", sm: "row" }}
          spacing={1}
          sx={{
            alignItems: { xs: "flex-start", sm: "center" },
            justifyContent: "space-between",
          }}
        >
          <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}>
            <CheckCircleOutlineIcon
              color={result.is_valid ? (warnings ? "warning" : "success") : "disabled"}
              fontSize="small"
            />
            <Typography variant="h3">Rule Check</Typography>
          </Stack>
          <Stack direction="row" spacing={0.75} sx={{ flexWrap: "wrap" }}>
            <Chip
              label={result.is_valid ? (warnings ? "Review warnings" : "Checks passed") : "Needs changes"}
              color={result.is_valid ? (warnings ? "warning" : "success") : "default"}
              size="small"
              sx={result.is_valid ? undefined : issueChipSx}
              {...(result.is_valid ? {} : ISSUE_CHIP_MARKER)}
            />
            <Chip
              label={`${issues} issues`}
              size="small"
              sx={issues ? issueChipSx : undefined}
              {...(issues ? ISSUE_CHIP_MARKER : {})}
            />
            <Chip
              label={`${warnings} warnings`}
              color={warnings ? "warning" : "default"}
              size="small"
            />
          </Stack>
        </Stack>

        <Alert severity={result.is_valid && !warnings ? "success" : "warning"} variant="outlined">
          {result.summary}
        </Alert>

        {totals.length > 0 && (
          <Stack direction="row" spacing={0.75} sx={{ flexWrap: "wrap" }}>
            {totals.map(([key, value]) => (
              <Chip key={key} label={`${formatKey(key)}: ${value}`} size="small" />
            ))}
          </Stack>
        )}

        {result.issues.length > 0 && (
          <Box>
            <Divider sx={{ mb: 1 }} />
            <List dense disablePadding>
              {result.issues.map((issue) => (
                <ListItem
                  key={`${issue.code}-${issue.message}`}
                  disableGutters
                  sx={{ alignItems: "flex-start", py: 0.75 }}
                >
                  <ListItemIcon sx={{ minWidth: 32, pt: 0.25 }}>
                    {issueIcon(issue)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Stack
                        direction="row"
                        spacing={0.75}
                        sx={{ alignItems: "center", flexWrap: "wrap" }}
                      >
                        <Typography variant="body2" sx={{ fontWeight: 700 }}>
                          {issue.message}
                        </Typography>
                        <Chip label={issue.code} size="small" variant="outlined" />
                      </Stack>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </Stack>
    </Paper>
  );
}
