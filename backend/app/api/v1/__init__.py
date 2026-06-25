"""Aggregator for all v1 routers."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import analysis, auth, careers, cv, dashboard, github, linkedin, mentor, portfolio, profiles, projects, quiz, roadmaps

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(mentor.router, prefix="/mentor", tags=["mentor"])
api_router.include_router(cv.router, prefix="/cv", tags=["cv"])
api_router.include_router(github.router, prefix="/github", tags=["github"])
api_router.include_router(linkedin.router, prefix="/linkedin", tags=["linkedin"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(careers.router, prefix="/careers", tags=["careers"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(roadmaps.router, prefix="/roadmaps", tags=["roadmaps"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
