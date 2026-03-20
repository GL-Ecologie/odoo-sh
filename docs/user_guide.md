# GL-Ecologie — Odoo Planning System: User Guide

**Version:** 1.1
**Last updated:** 2026-03-20
**Prepared by:** Ruiz Burgos Ecology and Software

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Getting Started](#2-getting-started)
3. [For All Users](#3-for-all-users)
   - 3.1 Your Employee Profile
   - 3.2 Filling In Your Availability
   - 3.3 Requesting an Open Shift
   - 3.4 Viewing Your Schedule
4. [For Managers & Project Leaders](#4-for-managers--project-leaders)
   - 4.1 Managing Employees
   - 4.2 Locations & Meeting Points
   - 4.3 Protocols
   - 4.4 Projects & Sub-projects
   - 4.5 Shift Types & Roles
   - 4.6 Creating & Publishing Shifts
   - 4.7 Assigning People to Shifts
   - 4.8 Validating Worked Hours
5. [Inventory & Tools](#5-inventory--tools)
6. [Reporting & Exports](#6-reporting--exports)
7. [Notifications & Approvals](#7-notifications--approvals)

---

## 1. Introduction

Brief description of the system, its purpose for GL-Ecologie, and the two main user roles (employee vs. manager/project leader).

---

## 2. Getting Started

- Accessing the system (URL, login)
- Navigating the main menu
- Switching language (NL/EN)
- Mobile vs. desktop use

---

## 3. For All Users

### 3.1 Your Employee Profile

- Where to find your profile
- Fields you can view/edit yourself:
  - Home address
  - Vehicle (yes/no)
  - Language (Dutch/other)
  - Max shifts per week
- Who to contact for changes

### 3.2 Filling In Your Availability

- Where to go: Planning → My Availability
- How to mark available / unavailable periods
- Recurring vs. one-time availability
- Deadlines and when to submit

### 3.3 Requesting an Open Shift

- Where to find open shifts: Planning → Open Shifts
- How to submit a request
- What happens after you request (approval flow, notification)
- You cannot self-assign — a manager confirms

### 3.4 Viewing Your Schedule

- Calendar view vs. list view
- Filtering by project or date
- What the shift details show (location, meeting point, role, time)

---

## 4. For Managers & Project Leaders

### 4.1 Managing Employees

- Creating and editing employee profiles
- Custom fields: vehicle, language, home address, max shifts/week
- Setting roles and permissions
- Deactivating an employee

### 4.2 Locations & Meeting Points

- Where locations are managed
- Creating a new location
- Adding meeting points to a location
- Linking a location to a project or shift

### 4.3 Protocols

> *A protocol defines the type of monitoring activity (e.g. Vleermuis regulier, Huismus SMP). It determines shift structure, required roles, and effort.*

- Where protocols are configured
- Fields per protocol: [list relevant fields]
- Linking a protocol to a project

### 4.4 Projects & Sub-projects

- Creating a project
- Required fields per project (protocol, location, period, roles)
- Creating sub-projects (nested under a parent project)
- Archiving or closing a project

### 4.5 Shift Types & Roles

- Available shift types (morning, evening, night, etc.)
- Roles per shift: Project Leader, Field Worker, [others]
- Assigning multiple roles per person on a shift

### 4.6 Creating & Publishing Shifts

- Creating a shift manually
- Generating recurring shifts
- Draft vs. published state
- Sending the schedule notification to employees (email)
- **Reminder field:** fill in the *Reminder* field on a shift to send the assigned employee an automatic preparation email 24 hours before the shift starts (e.g. "Remember to pick up keys from the office")

### 4.7 Assigning People to Shifts

- Opening the shift assignment panel
- How the system filters candidates:
  - Availability window
  - Role match
  - Max shifts/week not exceeded
- Assigning a person
- Handling shift requests from employees
- **Protocol visit window warning:** if a shift's date falls outside the protocol visit window defined on the linked task, an amber warning bar appears at the top of the shift form ("Shift date is outside the protocol visit window for the associated task"). This is informational only — it does not block saving the shift.

### 4.8 Registering & Validating Worked Hours

- **Register Hours button:** on a published shift with an assigned employee, click *Register Hours* to create a pre-filled timesheet entry (date, allocated hours, project, and task are filled in automatically). Only visible to the assigned employee and planning managers.
- Where employees log worked hours
- Project leader validation flow
- What happens after validation (locked, reportable)

---

## 5. Inventory & Tools

- Accessing the inventory
- Available item types: [list]
- Linking tools/materials to a shift
- Checking what is assigned to a shift
- Returning / unassigning items

---

## 6. Reporting & Exports

### 6.1 Planning Analysis

- Where to find it: Planning → Reporting → Planning Analysis
- Available measures: Allocated Time, Effective Time, Progress, Count
- Useful groupings:
  - Shifts per resource per week/month
  - Hours per project
  - Progress (%) per project
- Exporting to Excel

### 6.2 Availability Export

- Planning → Employee Availability → List view → Export
- What the export contains
- Typical use case

### 6.3 PDF Reports

- [If implemented] How to generate a PDF shift schedule
- [If implemented] How to generate a per-resource timesheet

---

## 7. Notifications & Approvals

- When employees receive email notifications (shift assigned, schedule published)
- Shift request approval flow (employee requests → manager approves/rejects)
- Worked hours validation notifications
- Where to check pending approvals

---

## Appendix

- Glossary (Dutch ↔ system terms if needed)
- Contact for support
