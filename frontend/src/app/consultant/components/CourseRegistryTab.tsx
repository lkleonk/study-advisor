"use client";

import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import LaunchOutlinedIcon from "@mui/icons-material/LaunchOutlined";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Collapse from "@mui/material/Collapse";
import FormControl from "@mui/material/FormControl";
import IconButton from "@mui/material/IconButton";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useMemo, useState } from "react";

import { getDummyCourseRegistry } from "@/app/consultant/dummy_data/courseRegistry";
import { useDegree } from "@/context/DegreeContext";
import { useSettings } from "@/context/SettingsContext";
import { getCourseOfferings } from "@/services/api";
import type { CourseOfferingArea, CourseOfferingsCatalogue, FirstSession } from "@/types/api";

const EMPTY_AREAS: CourseOfferingArea[] = [];

const SESSION_DATE_FORMAT = new Intl.DateTimeFormat("en-GB", {
  weekday: "short",
  day: "numeric",
  month: "short",
  year: "numeric",
  timeZone: "UTC",
});

// e.g. "Tue 13 Oct 2026, 16:00–18:00 · T9/Gr. Hörsaal (Takustr. 9)"
function formatSession(session: FirstSession) {
  const [year, month, day] = session.date.split("-").map(Number);
  let text = SESSION_DATE_FORMAT.format(new Date(Date.UTC(year, month - 1, day)));
  if (session.start && session.end) {
    text += `, ${session.start}–${session.end}`;
  }
  if (session.room) {
    text += ` · ${session.room}`;
  }
  return text;
}

function SessionLines({ label, sessions }: { label: string; sessions: FirstSession[] }) {
  if (sessions.length === 1) {
    return <Typography variant="body1">{`${label}: ${formatSession(sessions[0])}`}</Typography>;
  }
  return (
    <Box>
      <Typography variant="body1">{`${label}:`}</Typography>
      {sessions.map((session) => (
        <Typography key={`${session.date}-${session.start ?? ""}`} variant="body1" sx={{ pl: 2 }}>
          {formatSession(session)}
        </Typography>
      ))}
    </Box>
  );
}

function UebungLink({ url, title }: { url?: string | null; title: string }) {
  if (!url) {
    return null;
  }
  return (
    <Tooltip title="Open official Übung page">
      <IconButton
        component="a"
        href={url}
        target="_blank"
        rel="noreferrer"
        size="small"
        aria-label={`Open official Übung page for ${title}`}
      >
        <LaunchOutlinedIcon fontSize="small" />
      </IconButton>
    </Tooltip>
  );
}

// One Übung group fits on a line; several collapse behind a toggle.
function UebungLines({ groups, url, title }: { groups: FirstSession[]; url?: string | null; title: string }) {
  const [open, setOpen] = useState(false);
  if (groups.length === 0) {
    return null;
  }
  if (groups.length === 1) {
    return (
      <Stack direction="row" spacing={0.5} sx={{ alignItems: "center" }}>
        <SessionLines label="Übung" sessions={groups} />
        <UebungLink url={url} title={title} />
      </Stack>
    );
  }
  return (
    <Box>
      <Stack direction="row" spacing={0.5} sx={{ alignItems: "center" }}>
          <Button
          size="small"
          onClick={() => setOpen((value) => !value)}
          endIcon={open ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          aria-expanded={open}
          sx={{ px: 0, minWidth: 0 }}
        >
          {`Übungen (${groups.length} groups)`}
        </Button>
        <UebungLink url={url} title={title} />
      </Stack>
      <Collapse in={open}>
        {groups.map((group) => (
          <Typography key={`${group.date}-${group.start ?? ""}-${group.room ?? ""}`} variant="body1" sx={{ pl: 2 }}>
            {formatSession(group)}
          </Typography>
        ))}
      </Collapse>
    </Box>
  );
}

function uniqueCourseTypes(areas: CourseOfferingArea[]) {
  const seen = new Map<string, string>();
  for (const area of areas) {
    for (const courseType of area.course_types) {
      seen.set(courseType.id, courseType.label);
    }
  }
  return [...seen].map(([id, label]) => ({ id, label }));
}

export function CourseRegistryTab() {
  const { effectiveDegreeId } = useDegree();
  const { courseRegistryPreviewEnabled } = useSettings();
  const [catalogue, setCatalogue] = useState<CourseOfferingsCatalogue | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [semesterId, setSemesterId] = useState("");
  const [areaId, setAreaId] = useState("");
  const [courseTypeId, setCourseTypeId] = useState("");
  const [search, setSearch] = useState("");

  const loadOfferings = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const nextCatalogue = courseRegistryPreviewEnabled
        ? getDummyCourseRegistry(effectiveDegreeId)
        : await getCourseOfferings(effectiveDegreeId);
      if (!nextCatalogue) {
        throw new Error("No dummy Course Registry data exists for this degree.");
      }
      setCatalogue(nextCatalogue);
      setSemesterId(nextCatalogue.semesters[nextCatalogue.semesters.length - 1]?.id ?? "");
      setAreaId("");
      setCourseTypeId("");
      setSearch("");
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Failed to load course offerings.");
    } finally {
      setIsLoading(false);
    }
  }, [courseRegistryPreviewEnabled, effectiveDegreeId]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadOfferings();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [loadOfferings]);

  const selectedSemester = useMemo(
    () => catalogue?.semesters.find((semester) => semester.id === semesterId) ?? null,
    [catalogue, semesterId],
  );
  const availableAreas = selectedSemester?.areas ?? EMPTY_AREAS;
  const availableCourseTypes = useMemo(
    () => uniqueCourseTypes(areaId ? availableAreas.filter((area) => area.id === areaId) : availableAreas),
    [areaId, availableAreas],
  );
  const normalizedSearch = search.trim().toLocaleLowerCase();
  const visibleAreas = useMemo(
    () =>
      availableAreas
        .filter((area) => !areaId || area.id === areaId)
        .map((area) => ({
          ...area,
          course_types: area.course_types
            .filter((courseType) => !courseTypeId || courseType.id === courseTypeId)
            .map((courseType) => ({
              ...courseType,
              courses: courseType.courses.filter((course) =>
                course.title.toLocaleLowerCase().includes(normalizedSearch),
              ),
            }))
            .filter((courseType) => courseType.courses.length > 0),
        }))
        .filter((area) => area.course_types.length > 0),
    [areaId, availableAreas, courseTypeId, normalizedSearch],
  );
  const totalOfferings = catalogue?.semesters.reduce(
    (total, semester) =>
      total + semester.areas.reduce(
        (areaTotal, area) => areaTotal + area.course_types.reduce((typeTotal, type) => typeTotal + type.courses.length, 0),
        0,
      ),
    0,
  ) ?? 0;
  const visibleOfferings = visibleAreas.reduce(
    (total, area) => total + area.course_types.reduce((typeTotal, type) => typeTotal + type.courses.length, 0),
    0,
  );

  return (
    <Box sx={{ height: "100%", overflowY: "auto", px: { xs: 1.5, md: 3 }, py: 2 }}>
      <Stack spacing={2} sx={{ maxWidth: 1100, mx: "auto" }}>
        <Stack spacing={1}>
          <Box>
            <Typography variant="h2">Course Registry</Typography>
            {catalogue && (
              <Typography variant="body2" sx={{ color: "text.secondary", mt: 0.5 }}>
                {catalogue.degree_program} - {catalogue.regulation}
              </Typography>
            )}
          </Box>
        </Stack>

        {isLoading && (
          <Stack direction="row" spacing={1} sx={{ alignItems: "center", color: "text.secondary" }}>
            <CircularProgress size={18} />
            <Typography variant="body2">Loading course offerings</Typography>
          </Stack>
        )}

        {error && (
          <Alert
            severity="error"
            action={<Button onClick={() => void loadOfferings()}>Try again</Button>}
          >
            {error}
          </Alert>
        )}

        {catalogue && (
          <>
            {courseRegistryPreviewEnabled && (
              <Alert severity="warning" variant="outlined">
                Developer preview active. The listed offerings are bundled dummy data, not FU Berlin course catalogue data.
              </Alert>
            )}
            <Typography variant="caption" sx={{ color: "text.secondary" }}>
              Local offering data · Verify details in the official FU course catalogue.
            </Typography>

            <Stack direction="row" spacing={0.75} sx={{ flexWrap: "wrap" }}>
              <Chip label={`${totalOfferings} listed offering${totalOfferings === 1 ? "" : "s"}`} size="small" />
              {semesterId && <Chip label={`${visibleOfferings} matching`} size="small" variant="outlined" />}
            </Stack>

            {catalogue.semesters.length === 0 ? (
              <Alert severity="info">No course offerings are currently listed for this degree.</Alert>
            ) : (
              <>
                <Stack direction={{ xs: "column", sm: "row" }} spacing={1.25}>
                  <FormControl fullWidth size="small">
                    <InputLabel id="course-registry-semester-label">Semester</InputLabel>
                    <Select
                      labelId="course-registry-semester-label"
                      label="Semester"
                      value={semesterId}
                      onChange={(event) => {
                        const nextSemesterId = event.target.value;
                        const nextAreas =
                          catalogue.semesters.find((semester) => semester.id === nextSemesterId)?.areas ?? EMPTY_AREAS;
                        // Keep the area/type filters when they still exist in the new semester.
                        const keepArea = !areaId || nextAreas.some((area) => area.id === areaId);
                        const nextAreaId = keepArea ? areaId : "";
                        const typeAreas = nextAreaId ? nextAreas.filter((area) => area.id === nextAreaId) : nextAreas;
                        const keepType =
                          !courseTypeId || uniqueCourseTypes(typeAreas).some((type) => type.id === courseTypeId);
                        setSemesterId(nextSemesterId);
                        setAreaId(nextAreaId);
                        setCourseTypeId(keepType ? courseTypeId : "");
                      }}
                    >
                      {catalogue.semesters.map((semester) => (
                        <MenuItem key={semester.id} value={semester.id}>
                          {semester.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <FormControl fullWidth size="small">
                    <InputLabel id="course-registry-area-label">Area</InputLabel>
                    <Select
                      labelId="course-registry-area-label"
                      label="Area"
                      value={areaId}
                      onChange={(event) => {
                        setAreaId(event.target.value);
                        setCourseTypeId("");
                      }}
                    >
                      <MenuItem value="">All areas</MenuItem>
                      {availableAreas.map((area) => (
                        <MenuItem key={area.id} value={area.id}>
                          {area.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <FormControl fullWidth size="small">
                    <InputLabel id="course-registry-type-label">Course type</InputLabel>
                    <Select
                      labelId="course-registry-type-label"
                      label="Course type"
                      value={courseTypeId}
                      onChange={(event) => setCourseTypeId(event.target.value)}
                    >
                      <MenuItem value="">All types</MenuItem>
                      {availableCourseTypes.map((courseType) => (
                        <MenuItem key={courseType.id} value={courseType.id}>
                          {courseType.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Stack>

                <TextField
                  fullWidth
                  size="small"
                  label="Search course titles"
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                />

                {visibleAreas.length === 0 ? (
                  <Alert severity="info">No listed courses match these filters.</Alert>
                ) : (
                  <Stack spacing={3}>
                    {visibleAreas.map((area) => (
                      <Stack key={area.id} spacing={1.25}>
                        <Typography variant="h3">{area.label}</Typography>
                        {area.note && (
                          <Typography variant="body2" sx={{ color: "text.secondary" }}>
                            {area.note}
                          </Typography>
                        )}
                        {area.course_types.map((courseType) => (
                          <Stack key={courseType.id} spacing={1}>
                            <Typography variant="subtitle2" sx={{ color: "text.secondary" }}>
                              {courseType.label}
                            </Typography>
                            {courseType.courses.map((course) => (
                              <Card key={`${area.id}-${courseType.id}-${course.title}`} variant="outlined">
                                <CardContent>
                                  <Stack spacing={1}>
                                    <Stack
                                      direction={{ xs: "column", sm: "row" }}
                                      spacing={1}
                                      sx={{ alignItems: { xs: "flex-start", sm: "center" }, justifyContent: "space-between" }}
                                    >
                                      <Typography variant="h3" sx={{ fontSize: "1.15rem" }}>{course.title}</Typography>
                                      <Stack direction="row" spacing={0.75} sx={{ flexWrap: "wrap", alignItems: "center" }}>
                                        <Chip label={courseType.label} size="small" />
                                        {course.is_bachelor_module && <Chip label="Bachelor module" size="small" variant="outlined" />}
                                        {course.url && (
                                          <Tooltip title="Open official course page">
                                            <IconButton
                                              component="a"
                                              href={course.url}
                                              target="_blank"
                                              rel="noreferrer"
                                              size="small"
                                              aria-label={`Open official course page for ${course.title}`}
                                            >
                                              <LaunchOutlinedIcon fontSize="small" />
                                            </IconButton>
                                          </Tooltip>
                                        )}
                                      </Stack>
                                    </Stack>
                                    <Typography variant="body1" sx={{ color: "text.secondary" }}>
                                      {course.lp === null ? "LP not listed" : `${course.lp} LP`}
                                      {course.module_catalog_name ? ` - ${course.module_catalog_name}` : ""}
                                      {course.fu_module_code ? ` (${course.fu_module_code})` : ""}
                                    </Typography>
                                    {course.first_sessions && course.first_sessions.length > 0 && (
                                      <SessionLines
                                        label={course.first_sessions.length > 1 ? "First sessions" : "First session"}
                                        sessions={course.first_sessions}
                                      />
                                    )}
                                    <UebungLines groups={course.uebungen ?? []} url={course.uebung_url} title={course.title} />
                                  </Stack>
                                </CardContent>
                              </Card>
                            ))}
                          </Stack>
                        ))}
                      </Stack>
                    ))}
                  </Stack>
                )}
              </>
            )}
          </>
        )}
      </Stack>
    </Box>
  );
}
