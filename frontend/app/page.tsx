"use client";

import { useState } from "react";

interface Requirement {
  category: string;
  requirement: string;
  priority: string;
}

interface JobAnalysis {
  job_title: string;
  job_description: string;
  requirements: Requirement[];
  required_skills: string[];
  preferred_skills: string[];
  experience_level: string;
  location: string;
}

interface Evaluation {
  overall_assessment: string;
  unsupported_claims: string[];
  missing_requirements: string[];
  consistency_issues: string[];
  improvement_suggestions: string[];
  should_revise: boolean;
}

interface TailoredResume {
  target_title: string;
  summary: string;
  targeted_skills: string[];
  experience: {
    company: string;
    title: string;
    dates: string;
    bullets: string[];
  }[];
  projects: {
    name: string;
    bullets: string[];
  }[];
  awards_certifications?: {
    name: string;
  }[];
}

interface TailorResponse {
  target_job_title: string;
  job_analysis: JobAnalysis;
  tailored_resume: TailoredResume;
  evaluation: Evaluation;
  evidence_gaps: string[];
  revision_count: number;
}

export default function Home() {
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState<TailorResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function tailorResume() {
    if (jobDescription.trim().length < 50) {
      setError("Please enter a complete job description.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/tailor-resume",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            job_description: jobDescription,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.detail || "Resume tailoring failed."
        );
      }

      const data: TailorResponse = await response.json();

      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  }

  async function downloadResume() {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/tailor-resume-docx",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            job_description: jobDescription,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Could not generate DOCX.");
      }

      const blob = await response.blob();

      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");

      link.href = url;
      link.download = "Stuti_Bimali_Tailored_Resume.docx";

      document.body.appendChild(link);

      link.click();

      link.remove();

      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not download resume."
      );
    }
  }

  return (
    <main className="min-h-screen bg-neutral-950 text-white">
      <div className="mx-auto max-w-6xl px-6 py-12">

        {/* Header */}

        <header className="mb-10">
          <p className="mb-2 text-sm font-medium text-amber-400">
            AI / RAG / LANGGRAPH
          </p>

          <h1 className="text-4xl font-bold tracking-tight">
            AI Resume Tailor
          </h1>

          <p className="mt-3 max-w-2xl text-neutral-400">
            Evidence-grounded resume tailoring using Gemini,
            LangChain, LangGraph, RAG and FAISS.
          </p>
        </header>

        {/* Job Description */}

        <section className="rounded-2xl border border-neutral-800 bg-neutral-900 p-6">

          <label className="mb-3 block text-sm font-semibold">
            Job Description
          </label>

          <textarea
            value={jobDescription}
            onChange={(e) =>
              setJobDescription(e.target.value)
            }
            placeholder="Paste the complete job description here..."
            className="min-h-[280px] w-full resize-y rounded-xl border border-neutral-700 bg-neutral-950 p-4 text-sm outline-none placeholder:text-neutral-600 focus:border-amber-400"
          />

          <div className="mt-4 flex items-center justify-between">

            <span className="text-xs text-neutral-500">
              {jobDescription.length} characters
            </span>

            <button
              onClick={tailorResume}
              disabled={loading}
              className="rounded-xl bg-amber-400 px-6 py-3 text-sm font-semibold text-black transition hover:bg-amber-300 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading
                ? "Tailoring Resume..."
                : "Tailor My Resume"}
            </button>

          </div>

          {error && (
            <div className="mt-4 rounded-xl border border-red-900 bg-red-950/40 p-4 text-sm text-red-300">
              {error}
            </div>
          )}

        </section>

        {/* Results */}

        {result && (
          <div className="mt-8 space-y-6">

            {/* Job Analysis */}

            <section className="rounded-2xl border border-neutral-800 bg-neutral-900 p-6">

              <p className="text-xs font-medium uppercase tracking-wider text-neutral-500">
                Job Analysis
              </p>

              <h2 className="mt-2 text-2xl font-bold">
                {result.target_job_title}
              </h2>

              <p className="mt-2 text-sm text-neutral-400">
                {result.job_analysis.experience_level}
                {result.job_analysis.location &&
                  ` • ${result.job_analysis.location}`}
              </p>

              <div className="mt-5 flex flex-wrap gap-2">
                {result.job_analysis.required_skills.map(
                  (skill) => (
                    <span
                      key={skill}
                      className="rounded-full border border-neutral-700 px-3 py-1 text-xs"
                    >
                      {skill}
                    </span>
                  )
                )}
              </div>

            </section>

            {/* Evidence Gaps */}

            <section className="rounded-2xl border border-neutral-800 bg-neutral-900 p-6">

              <p className="text-xs font-medium uppercase tracking-wider text-neutral-500">
                Evidence Check
              </p>

              {result.evidence_gaps.length === 0 ? (
                <p className="mt-3 text-sm text-green-400">
                  No major evidence gaps identified.
                </p>
              ) : (
                <ul className="mt-3 space-y-2">
                  {result.evidence_gaps.map(
                    (gap, index) => (
                      <li
                        key={index}
                        className="text-sm text-amber-300"
                      >
                        ⚠ {gap}
                      </li>
                    )
                  )}
                </ul>
              )}

            </section>

            {/* Resume */}

            <section className="rounded-2xl border border-neutral-800 bg-neutral-900 p-6">

              <div className="flex items-start justify-between gap-4">

                <div>
                  <p className="text-xs font-medium uppercase tracking-wider text-neutral-500">
                    Tailored Resume
                  </p>

                  <h2 className="mt-2 text-2xl font-bold">
                    {result.tailored_resume.target_title}
                  </h2>
                </div>

                <button
                  onClick={downloadResume}
                  className="rounded-xl border border-neutral-700 px-4 py-2 text-sm font-semibold hover:border-amber-400"
                >
                  Download DOCX
                </button>

              </div>

              {/* Summary */}

              <div className="mt-6">
                <h3 className="text-sm font-semibold">
                  Summary
                </h3>

                <p className="mt-2 text-sm leading-6 text-neutral-300">
                  {result.tailored_resume.summary}
                </p>
              </div>

              {/* Skills */}

              <div className="mt-6">
                <h3 className="text-sm font-semibold">
                  Targeted Skills
                </h3>

                <div className="mt-3 flex flex-wrap gap-2">
                  {result.tailored_resume.targeted_skills.map(
                    (skill) => (
                      <span
                        key={skill}
                        className="rounded-lg bg-neutral-800 px-3 py-1.5 text-xs"
                      >
                        {skill}
                      </span>
                    )
                  )}
                </div>
              </div>

              {/* Experience */}

              <div className="mt-8">
                <h3 className="text-sm font-semibold">
                  Professional Experience
                </h3>

                <div className="mt-4 space-y-6">
                  {result.tailored_resume.experience.map(
                    (experience, index) => (
                      <div key={index}>

                        <div className="flex flex-wrap justify-between gap-2">
                          <div>
                            <p className="font-semibold">
                              {experience.company}
                            </p>

                            <p className="text-sm text-neutral-400">
                              {experience.title}
                            </p>
                          </div>

                          <p className="text-xs text-neutral-500">
                            {experience.dates}
                          </p>
                        </div>

                        <ul className="mt-3 space-y-2">
                          {experience.bullets.map(
                            (bullet, bulletIndex) => (
                              <li
                                key={bulletIndex}
                                className="text-sm leading-5 text-neutral-300"
                              >
                                • {bullet}
                              </li>
                            )
                          )}
                        </ul>

                      </div>
                    )
                  )}
                </div>
              </div>

              {/* Projects */}

              <div className="mt-8">
                <h3 className="text-sm font-semibold">
                  Projects
                </h3>

                <div className="mt-4 space-y-5">
                  {result.tailored_resume.projects.map(
                    (project, index) => (
                      <div key={index}>

                        <p className="font-semibold">
                          {project.name}
                        </p>

                        <ul className="mt-2 space-y-2">
                          {project.bullets.map(
                            (bullet, bulletIndex) => (
                              <li
                                key={bulletIndex}
                                className="text-sm text-neutral-300"
                              >
                                • {bullet}
                              </li>
                            )
                          )}
                        </ul>

                      </div>
                    )
                  )}
                </div>
              </div>

              {/* Awards */}

              {result.tailored_resume
                .awards_certifications &&
                result.tailored_resume
                  .awards_certifications.length > 0 && (
                  <div className="mt-8">

                    <h3 className="text-sm font-semibold">
                      Awards & Certifications
                    </h3>

                    <ul className="mt-3 space-y-2">
                      {result.tailored_resume
                        .awards_certifications
                        .map((item, index) => (
                          <li
                            key={index}
                            className="text-sm text-neutral-300"
                          >
                            • {item.name}
                          </li>
                        ))}
                    </ul>

                  </div>
                )}

            </section>

            {/* Evaluation */}

            <section className="rounded-2xl border border-neutral-800 bg-neutral-900 p-6">

              <p className="text-xs font-medium uppercase tracking-wider text-neutral-500">
                Resume Evaluator
              </p>

              <p className="mt-3 text-sm leading-6 text-neutral-300">
                {result.evaluation.overall_assessment}
              </p>

              {result.evaluation.unsupported_claims.length > 0 && (
                <div className="mt-5">
                  <h3 className="text-sm font-semibold text-red-300">
                    Unsupported Claims
                  </h3>

                  <ul className="mt-2 space-y-1">
                    {result.evaluation.unsupported_claims.map(
                      (item, index) => (
                        <li
                          key={index}
                          className="text-sm text-neutral-400"
                        >
                          • {item}
                        </li>
                      )
                    )}
                  </ul>
                </div>
              )}

              {result.evaluation.improvement_suggestions.length > 0 && (
                <div className="mt-5">
                  <h3 className="text-sm font-semibold">
                    Improvement Suggestions
                  </h3>

                  <ul className="mt-2 space-y-1">
                    {result.evaluation.improvement_suggestions.map(
                      (item, index) => (
                        <li
                          key={index}
                          className="text-sm text-neutral-400"
                        >
                          • {item}
                        </li>
                      )
                    )}
                  </ul>
                </div>
              )}

              <div className="mt-5 text-xs text-neutral-500">
                Revision cycles: {result.revision_count}
              </div>

            </section>

          </div>
        )}

      </div>
    </main>
  );
}