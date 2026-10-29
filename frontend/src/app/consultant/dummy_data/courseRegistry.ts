import type { CourseOfferingsCatalogue } from "@/types/api";

/**
 * Frontend-only dummy data for the developer Course Registry preview.
 * It intentionally contains fictional example offerings and must never be
 * presented as FU Berlin catalogue data.
 */
export const COURSE_REGISTRY_DUMMY_CATALOGUES: Record<string, CourseOfferingsCatalogue> = {
  msc_informatik: {
    degree_program: "M.Sc. Informatik",
    regulation: "Developer preview",
    source_note: "Dummy developer preview data bundled with the frontend. It is not FU Berlin course catalogue data.",
    semesters: [
      {
        id: "sose26",
        label: "SoSe 2026",
        areas: [
          {
            id: "technical",
            label: "Technical Informatics",
            course_types: [
              {
                id: "vl",
                label: "Lecture",
                courses: [
                  {
                    title: "Example: Distributed Systems",
                    module_catalog_name: "Example technical module",
                    lp: 10,
                    first_sessions: [
                      { date: "2026-04-13", start: "10:00", end: "12:00", room: "Dummy room" },
                      { date: "2026-04-15", start: "10:00", end: "12:00", room: "Dummy room" },
                    ],
                    uebungen: [
                      { date: "2026-04-14", start: "08:00", end: "10:00", room: "Dummy room A" },
                      { date: "2026-04-14", start: "12:00", end: "14:00", room: "Dummy room B" },
                      { date: "2026-04-16", start: "14:00", end: "16:00", room: "Dummy room A" },
                    ],
                    uebung_url: "https://example.com/course-registry-preview-uebung",
                    url: "https://example.com/course-registry-preview",
                  },
                ],
              },
              {
                id: "swp",
                label: "Software project",
                courses: [
                  {
                    title: "Example: Systems Project",
                    module_catalog_name: "Example software project",
                    lp: null,
                    first_sessions: [],
                    is_bachelor_module: true,
                  },
                ],
              },
            ],
          },
          {
            id: "practical",
            label: "Practical Informatics",
            course_types: [
              {
                id: "seminar",
                label: "Seminar",
                courses: [
                  {
                    title: "Example: Applied Computing Seminar",
                    module_catalog_name: "Example practical module",
                    lp: 5,
                    first_sessions: [{ date: "2026-04-14", start: "14:00", end: "16:00", room: "Dummy room" }],
                  },
                ],
              },
            ],
          },
        ],
      },
    ],
  },
  msc_data_science: {
    degree_program: "M.Sc. Data Science",
    regulation: "Developer preview",
    source_note: "Dummy developer preview data bundled with the frontend. It is not FU Berlin course catalogue data.",
    semesters: [
      {
        id: "sose26",
        label: "SoSe 2026",
        areas: [
          {
            id: "grundlagen",
            label: "Foundations",
            course_types: [
              {
                id: "vl",
                label: "Lecture",
                courses: [
                  {
                    title: "Example: Statistical Learning",
                    module_catalog_name: "Example foundations module",
                    lp: 10,
                    first_sessions: [{ date: "2026-04-15", start: "12:00", end: "14:00", room: "Dummy room" }],
                    uebungen: [{ date: "2026-04-17", start: "10:00", end: "12:00", room: "Dummy room" }],
                  },
                ],
              },
            ],
          },
          {
            id: "technologies",
            label: "Technologies",
            course_types: [
              {
                id: "seminar",
                label: "Seminar",
                courses: [
                  {
                    title: "Example: Data Platform Seminar",
                    module_catalog_name: "Example technologies module",
                    lp: 5,
                    first_sessions: [],
                  },
                ],
              },
            ],
          },
        ],
      },
    ],
  },
};

export function getDummyCourseRegistry(degreeId: string): CourseOfferingsCatalogue | null {
  return COURSE_REGISTRY_DUMMY_CATALOGUES[degreeId] ?? null;
}
