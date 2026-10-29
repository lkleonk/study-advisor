"use client";

import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutlineOutlined";
import FactCheckOutlinedIcon from "@mui/icons-material/FactCheckOutlined";
import MenuBookOutlinedIcon from "@mui/icons-material/MenuBookOutlined";
import RuleOutlinedIcon from "@mui/icons-material/RuleOutlined";
import SchoolOutlinedIcon from "@mui/icons-material/SchoolOutlined";
import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";
import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import Typography from "@mui/material/Typography";
import NextLink from "next/link";
import { useEffect, useState, type ReactElement } from "react";

import { DEGREE_STORAGE_KEY, useDegree } from "@/context/DegreeContext";
import { useUsage } from "@/context/UsageContext";
import { deleteSession } from "@/services/api";
import type { RuleCheckResult, StudyPlan, UsageResponse } from "@/types/api";

import { ChatTab } from "./ChatTab";
import { ChatExportDialog } from "./ChatExportDialog";
import { downloadChat, type ChatExportFormat } from "./chatExport";
import { loadStoredChatMessages, type ChatMessage } from "./chatMessages";
import { ChatErrorDialog, DEFAULT_CHAT_ERROR_MESSAGE } from "./ChatErrorDialog";
import { CourseRegistryTab } from "./CourseRegistryTab";
import { DegreeRulesTab } from "./DegreeRulesTab";
import { DegreeSwitchDialog } from "./DegreeSwitchDialog";
import { LowRequestWarningDialog } from "./LowRequestWarningDialog";
import { QuotaExhaustedDialog, type QuotaExhaustedScope } from "./QuotaExhaustedDialog";
import { RequestUsageDialog } from "./RequestUsageDialog";
import { SettingsTab } from "./SettingsTab";
import { StudyPlanTab } from "./StudyPlanTab";
import {
  CHAT_MESSAGES_STORAGE_KEY,
  CURRENT_WELCOME_VERSION,
  SESSION_ID_STORAGE_KEY,
  WELCOME_VERSION_STORAGE_KEY,
} from "./storage";
import { WelcomeDialog } from "./WelcomeDialog";

type TabId = "chat" | "study-plan" | "degree-rules" | "course-registry" | "settings";

/** Viewport widths where the header switches layout; see the Tabs sx below. */
const HEADER_ONE_ROW_MIN_WIDTH = 800;
const HEADER_TAB_ICONS_MIN_WIDTH = 1000;

const tabs: { label: string; icon: ReactElement; id: TabId }[] = [
  { label: "Chat", icon: <ChatBubbleOutlineIcon />, id: "chat" },
  { label: "Study Plan", icon: <FactCheckOutlinedIcon />, id: "study-plan" },
  { label: "Degree Rules", icon: <RuleOutlinedIcon />, id: "degree-rules" },
  { label: "Course Registry", icon: <MenuBookOutlinedIcon />, id: "course-registry" },
  { label: "Settings", icon: <SettingsOutlinedIcon />, id: "settings" },
];

const DAILY_REQUEST_ALLOWANCE_PREVIEW: UsageResponse = {
  limit: 25,
  used: 13,
  remaining: 12,
  reset_at: "2026-07-13T00:00:00Z",
  service: { limit: 150, used: 111, remaining: 39 },
  session_inactivity_ttl_seconds: 172800,
  diagnostic_tracing_enabled: false,
  quota_scope: "client_ip",
};

function readStoredSessionId() {
  if (typeof window === "undefined") {
    return null;
  }
  const sessionId = window.sessionStorage.getItem(SESSION_ID_STORAGE_KEY);
  if (sessionId === "dummy-session") {
    window.sessionStorage.removeItem(SESSION_ID_STORAGE_KEY);
    return null;
  }
  return sessionId;
}

function readStoredRuleCheck(): RuleCheckResult | null {
  const latest = [...loadStoredChatMessages()].reverse().find((message) => message.ruleCheckResult);
  return latest?.ruleCheckResult ?? null;
}

function readStoredStudyPlan(): StudyPlan | null {
  const latest = [...loadStoredChatMessages()].reverse().find((message) => message.parsedStudyPlan);
  return latest?.parsedStudyPlan ?? null;
}

export function ConsultantShell() {
  const { usage } = useUsage();
  const { degreeId, effectiveDegreeId, degrees, selectDegree } = useDegree();
  const [selectedTab, setSelectedTab] = useState<TabId>("chat");
  const [pendingDegreeId, setPendingDegreeId] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [latestRuleCheck, setLatestRuleCheck] = useState<RuleCheckResult | null>(null);
  const [latestStudyPlan, setLatestStudyPlan] = useState<StudyPlan | null>(null);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [resetToken, setResetToken] = useState(0);
  const [usageDialogOpen, setUsageDialogOpen] = useState(false);
  const [usagePreviewDialogOpen, setUsagePreviewDialogOpen] = useState(false);
  const [failedChatPreviewOpen, setFailedChatPreviewOpen] = useState(false);
  const [welcomeOpen, setWelcomeOpen] = useState(false);
  const [welcomeChecked, setWelcomeChecked] = useState(false);
  const [lowRequestWarningOpen, setLowRequestWarningOpen] = useState(false);
  const [quotaExhaustedOpen, setQuotaExhaustedOpen] = useState(false);
  // The visitor's own limit wins: when both are used up, that is the truthful reason.
  const quotaExhaustedScope: QuotaExhaustedScope | null = !usage
    ? null
    : usage.remaining <= 0
      ? "user"
      : usage.service.remaining <= 0
        ? "service"
        : null;
  const [chatExportOpen, setChatExportOpen] = useState(false);
  const [chatMessagesToExport, setChatMessagesToExport] = useState<ChatMessage[]>([]);

  // The Study Plan tab only exists for degrees with trusted plan validation.
  const planValidationEnabled =
    degrees.find((degree) => degree.id === effectiveDegreeId)?.plan_validation_enabled ?? false;
  const visibleTabs = tabs.filter((tab) => tab.id !== "study-plan" || planValidationEnabled);
  const activeTab = visibleTabs.some((tab) => tab.id === selectedTab) ? selectedTab : "chat";

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setSessionId(readStoredSessionId());
      setLatestRuleCheck(readStoredRuleCheck());
      setLatestStudyPlan(readStoredStudyPlan());
    }, 0);

    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      const seenVersion = window.localStorage.getItem(WELCOME_VERSION_STORAGE_KEY);
      const hasStoredDegree = Boolean(window.localStorage.getItem(DEGREE_STORAGE_KEY));
      setWelcomeOpen(seenVersion !== CURRENT_WELCOME_VERSION || !hasStoredDegree);
      setWelcomeChecked(true);
    }, 0);

    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (
      !welcomeChecked ||
      welcomeOpen ||
      !usage ||
      usage.used === 0 ||
      usage.remaining <= 0 ||
      usage.remaining > 10
    ) {
      return;
    }

    const warningKey = `fu-consultant-low-request-warning-${usage.reset_at}`;
    if (window.sessionStorage.getItem(warningKey)) {
      return;
    }
    window.sessionStorage.setItem(warningKey, "shown");
    const timer = window.setTimeout(() => setLowRequestWarningOpen(true), 0);
    return () => window.clearTimeout(timer);
  }, [usage, welcomeChecked, welcomeOpen]);

  useEffect(() => {
    if (!welcomeChecked || welcomeOpen || !quotaExhaustedScope || !usage) {
      return;
    }

    const exhaustedKey = `fu-consultant-quota-exhausted-${quotaExhaustedScope}-${usage.reset_at}`;
    if (window.sessionStorage.getItem(exhaustedKey)) {
      return;
    }
    window.sessionStorage.setItem(exhaustedKey, "shown");
    const timer = window.setTimeout(() => setQuotaExhaustedOpen(true), 0);
    return () => window.clearTimeout(timer);
  }, [quotaExhaustedScope, usage, welcomeChecked, welcomeOpen]);

  const closeWelcome = (selectedDegreeId: string) => {
    window.localStorage.setItem(WELCOME_VERSION_STORAGE_KEY, CURRENT_WELCOME_VERSION);
    if (usage && usage.used > 0 && usage.remaining <= 10) {
      window.sessionStorage.setItem(
        `fu-consultant-low-request-warning-${usage.reset_at}`,
        "shown",
      );
    }
    // A different choice than the stored one invalidates any existing
    // degree-specific session data.
    if (selectedDegreeId !== degreeId && (sessionId || chatMessages.length > 0)) {
      void handleClearLocalState();
    }
    selectDegree(selectedDegreeId);
    setWelcomeOpen(false);
  };

  const handleClearLocalState = async () => {
    if (sessionId) {
      try {
        await deleteSession(sessionId);
      } catch {
        // The backend session expires on its own; local reset must not block on it.
      }
    }
    window.sessionStorage.removeItem(SESSION_ID_STORAGE_KEY);
    window.sessionStorage.removeItem(CHAT_MESSAGES_STORAGE_KEY);
    setSessionId(null);
    setLatestRuleCheck(null);
    setLatestStudyPlan(null);
    setChatMessages([]);
    setResetToken((current) => current + 1);
    setSelectedTab("chat");
  };

  const requestDegreeSwitch = (nextDegreeId: string) => {
    if (nextDegreeId === effectiveDegreeId) {
      return;
    }
    if (!sessionId && chatMessages.length === 0) {
      // Nothing to lose; switch immediately.
      selectDegree(nextDegreeId);
      setResetToken((current) => current + 1);
      return;
    }
    setPendingDegreeId(nextDegreeId);
  };

  const confirmDegreeSwitch = async () => {
    const target = pendingDegreeId;
    setPendingDegreeId(null);
    if (!target) {
      return;
    }
    await handleClearLocalState();
    selectDegree(target);
  };

  const openChatExport = (messages = chatMessages) => {
    const messagesToExport = messages.length > 0 ? messages : loadStoredChatMessages();
    if (messagesToExport.length === 0) {
      return;
    }
    setChatMessagesToExport(messagesToExport);
    setChatExportOpen(true);
  };

  const downloadSelectedChatFormat = (format: ChatExportFormat) => {
    downloadChat(chatMessagesToExport, format);
    setChatExportOpen(false);
  };

  return (
    <Box
      sx={{
        height: "100dvh",
        minHeight: 0,
        display: "flex",
        flexDirection: "column",
        bgcolor: "background.default",
        color: "text.primary",
      }}
    >
      <Box
        component="header"
        data-print-hidden="true"
        sx={{
          flexShrink: 0,
          bgcolor: "background.paper",
          borderBottom: 1,
          borderColor: "divider",
        }}
      >
        <Box
          sx={{
            px: { xs: 1.5, md: 3 },
            display: "flex",
            flexWrap: "wrap",
            alignItems: "center",
            justifyContent: "space-between",
            columnGap: 1.5,
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 1, py: 1 }}>
            <SchoolOutlinedIcon color="primary" />
            <Box>
              <Typography variant="h1">Modulio</Typography>
              {degrees.length > 1 ? (
                // Every degree name is rendered invisibly in the same grid cell, so the
                // cell is always as wide as the longest name and the tabs never shift
                // when the degree changes. The select itself hugs the current name.
                <Box sx={{ display: "grid", "& > *": { gridArea: "1 / 1" } }}>
                  {degrees.map((degree) => (
                    <Box
                      key={degree.id}
                      component="span"
                      aria-hidden
                      sx={{
                        visibility: "hidden",
                        height: 0,
                        overflow: "hidden",
                        whiteSpace: "nowrap",
                        typography: "body2",
                        pr: 3,
                      }}
                    >
                      {degree.display_name}
                    </Box>
                  ))}
                  <Select
                    value={degrees.some((degree) => degree.id === effectiveDegreeId) ? effectiveDegreeId : ""}
                    onChange={(event) => requestDegreeSwitch(event.target.value)}
                    variant="standard"
                    disableUnderline
                    inputProps={{ "aria-label": "Degree program" }}
                    sx={{
                      justifySelf: "start",
                      fontSize: (theme) => theme.typography.body2.fontSize,
                      color: "text.secondary",
                      "& .MuiSelect-select": { py: 0, pr: 3 },
                    }}
                  >
                    {degrees.map((degree) => (
                      <MenuItem key={degree.id} value={degree.id}>
                        {degree.display_name}
                      </MenuItem>
                    ))}
                  </Select>
                </Box>
              ) : (
                <Typography variant="body2" sx={{ color: "text.secondary" }}>
                  {degrees[0]?.display_name ?? "Degree program"}
                </Typography>
              )}
            </Box>
          </Box>
          <Tabs
            value={activeTab}
            onChange={(_, nextTab: TabId) => setSelectedTab(nextTab)}
            sx={{
              // Header steps, measured with the 5-tab degrees (brand ~160px, tabs 675px with
              // icons / 515px without):
              //   >= 1000px   one row, icon + label
              //   800-999px   one row, label only
              //   600-799px   tabs on their own row, icon + label
              //   < 600px     tabs on their own row, icon only (label hidden on the Tab)
              order: 3,
              width: "100%",
              [`@media (min-width: ${HEADER_ONE_ROW_MIN_WIDTH}px)`]: {
                order: 0,
                width: "auto",
                flex: "1 1 auto",
                alignSelf: "stretch",
              },
              [`@media (min-width: ${HEADER_ONE_ROW_MIN_WIDTH}px) and (max-width: ${HEADER_TAB_ICONS_MIN_WIDTH - 0.05}px)`]: {
                "& .MuiTab-icon": { display: "none" },
              },
              minHeight: { xs: 44, sm: 52 },
              "& .MuiTabs-scroller": {
                height: "100%",
              },
              "& .MuiTabs-list": {
                height: "100%",
              },
              "& .MuiTab-root": {
                // Size by label and share the spare width; labels never wrap, so the
                // header wraps to two rows instead of breaking a label.
                flex: "1 1 auto",
                height: "100%",
                whiteSpace: "nowrap",
              },
            }}
          >
            {visibleTabs.map((tab) => (
              <Tab
                key={tab.id}
                value={tab.id}
                icon={tab.icon}
                iconPosition="start"
                label={
                  <Box component="span" sx={{ display: { xs: "none", sm: "inline" } }}>
                    {tab.label}
                  </Box>
                }
                id={`${tab.id}-tab`}
                aria-label={tab.label}
                aria-controls={`${tab.id}-panel`}
                sx={{
                  minWidth: 0,
                  minHeight: { xs: 44, sm: 52 },
                  px: { xs: 0.75, sm: 2 },
                  "& .MuiTab-icon": {
                    mr: { xs: 0, sm: 1 },
                  },
                }}
              />
            ))}
          </Tabs>
        </Box>
      </Box>

      <Box component="main" sx={{ flex: 1, minHeight: 0 }}>
        <Box
          id="chat-panel"
          role="tabpanel"
          hidden={activeTab !== "chat"}
          aria-labelledby="chat-tab"
          sx={{ height: "100%", minHeight: 0 }}
        >
          {activeTab === "chat" && (
            <ChatTab
              key={resetToken}
              sessionId={sessionId}
              onSessionIdChange={setSessionId}
              onRuleCheckResult={setLatestRuleCheck}
              onStudyPlan={setLatestStudyPlan}
              onMessagesChange={setChatMessages}
              onOpenUsage={() => setUsageDialogOpen(true)}
              onDownloadChat={() => openChatExport()}
              onContinueElsewhere={() => setQuotaExhaustedOpen(true)}
            />
          )}
        </Box>
        {planValidationEnabled && (
          <Box
            id="study-plan-panel"
            role="tabpanel"
            hidden={activeTab !== "study-plan"}
            aria-labelledby="study-plan-tab"
            sx={{ height: "100%", minHeight: 0 }}
          >
            {activeTab === "study-plan" && (
              <StudyPlanTab
                latestRuleCheck={latestRuleCheck}
                latestStudyPlan={latestStudyPlan}
                sessionId={sessionId}
                onSessionIdChange={setSessionId}
                onRuleCheckResult={setLatestRuleCheck}
                onStudyPlan={setLatestStudyPlan}
              />
            )}
          </Box>
        )}
        <Box
          id="degree-rules-panel"
          role="tabpanel"
          hidden={activeTab !== "degree-rules"}
          aria-labelledby="degree-rules-tab"
          sx={{ height: "100%", minHeight: 0 }}
        >
          {activeTab === "degree-rules" && <DegreeRulesTab />}
        </Box>
        <Box
          id="course-registry-panel"
          role="tabpanel"
          hidden={activeTab !== "course-registry"}
          aria-labelledby="course-registry-tab"
          sx={{ height: "100%", minHeight: 0 }}
        >
          {activeTab === "course-registry" && <CourseRegistryTab />}
        </Box>
        <Box
          id="settings-panel"
          role="tabpanel"
          hidden={activeTab !== "settings"}
          aria-labelledby="settings-tab"
          sx={{ height: "100%", minHeight: 0 }}
        >
          {activeTab === "settings" && (
            <SettingsTab
              sessionId={sessionId}
              onClearLocalState={handleClearLocalState}
              onShowFailedChatRequest={() => setFailedChatPreviewOpen(true)}
              onShowUsagePreview={() => setUsagePreviewDialogOpen(true)}
              onOpenUsage={() => setUsageDialogOpen(true)}
              onShowWelcome={() => setWelcomeOpen(true)}
              onOpenChatExport={() => openChatExport()}
            />
          )}
        </Box>
      </Box>
      <Box
        component="footer"
        data-print-hidden="true"
        sx={{
          flexShrink: 0,
          borderTop: 1,
          borderColor: "divider",
          bgcolor: "background.paper",
          px: 2,
          py: 0.75,
        }}
      >
        <Box
          component="nav"
          aria-label="Rechtliche Hinweise"
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexWrap: "wrap",
            columnGap: 1,
            rowGap: 0.25,
            color: "text.secondary",
            fontSize: 12,
            "& a": { whiteSpace: "nowrap" },
          }}
        >
          <Link component={NextLink} href="/impressum" color="inherit" underline="hover">
            Impressum
          </Link>
          <Box component="span" aria-hidden sx={{ opacity: 0.55 }}>
            /
          </Box>
          <Link component={NextLink} href="/datenschutz" color="inherit" underline="hover">
            Datenschutz
          </Link>
          <Box component="span" aria-hidden sx={{ opacity: 0.55 }}>
            /
          </Box>
          <Link
            href="https://github.com/lkleonk/study-advisor"
            target="_blank"
            rel="noopener noreferrer"
            color="inherit"
            underline="hover"
          >
            GitHub
          </Link>
          <Box component="span" aria-hidden sx={{ opacity: 0.55 }}>
            /
          </Box>
          <Link
            href="https://getwizardflow.com"
            target="_blank"
            rel="noopener noreferrer"
            color="inherit"
            underline="hover"
          >
            Built with WizardFlow ↗
          </Link>
        </Box>
      </Box>
      <WelcomeDialog
        open={welcomeOpen}
        onClose={closeWelcome}
        onViewUsage={(selectedDegreeId) => {
          closeWelcome(selectedDegreeId);
          setUsageDialogOpen(true);
        }}
      />
      <DegreeSwitchDialog
        open={pendingDegreeId !== null}
        targetDegree={degrees.find((degree) => degree.id === pendingDegreeId) ?? null}
        hasChatMessages={chatMessages.length > 0}
        hasStudyPlan={latestStudyPlan !== null}
        onDownloadChat={() => openChatExport(chatMessages)}
        onOpenStudyPlan={
          planValidationEnabled
            ? () => {
                setPendingDegreeId(null);
                setSelectedTab("study-plan");
              }
            : undefined
        }
        onCancel={() => setPendingDegreeId(null)}
        onConfirm={() => void confirmDegreeSwitch()}
      />
      <LowRequestWarningDialog
        open={lowRequestWarningOpen}
        remaining={usage?.remaining ?? 0}
        onClose={() => setLowRequestWarningOpen(false)}
        onViewUsage={() => {
          setLowRequestWarningOpen(false);
          setUsageDialogOpen(true);
        }}
      />
      <QuotaExhaustedDialog
        open={quotaExhaustedOpen}
        scope={quotaExhaustedScope ?? "user"}
        resetAt={usage?.reset_at ?? null}
        conversation={chatMessages}
        onClose={() => setQuotaExhaustedOpen(false)}
        onOpenDegreeRules={() => {
          setQuotaExhaustedOpen(false);
          setSelectedTab("degree-rules");
        }}
      />
      <RequestUsageDialog open={usageDialogOpen} onClose={() => setUsageDialogOpen(false)} />
      <RequestUsageDialog
        open={usagePreviewDialogOpen}
        onClose={() => setUsagePreviewDialogOpen(false)}
        usageOverride={DAILY_REQUEST_ALLOWANCE_PREVIEW}
      />
      <ChatErrorDialog
        open={failedChatPreviewOpen}
        message={DEFAULT_CHAT_ERROR_MESSAGE}
        onClose={() => setFailedChatPreviewOpen(false)}
      />
      <ChatExportDialog
        open={chatExportOpen}
        messages={chatMessagesToExport}
        onClose={() => setChatExportOpen(false)}
        onDownload={downloadSelectedChatFormat}
      />
    </Box>
  );
}
