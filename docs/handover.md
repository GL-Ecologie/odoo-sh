# GL-Ecologie Odoo Module — Handover Document

**Module:** `gl_custom_module`
**Version:** 1.0.6
**Author:** Julian Ruiz Burgos
**Website:** https://www.gl-ecologie.nl
**Last reviewed:** 2026-03-20

---

## Table of Contents

1. [Overview](#1-overview)
2. [Repository Layout](#2-repository-layout)
3. [Module Dependencies](#3-module-dependencies)
4. [Feature Areas](#4-feature-areas)
5. [Custom Models](#5-custom-models)
6. [Inherited Models](#6-inherited-models)
7. [Security Model](#7-security-model)
8. [Frontend (OWL / JS / SCSS)](#8-frontend-owl--js--scss)
9. [Key Architectural Decisions](#9-key-architectural-decisions)
10. [Known Issues & TODOs](#10-known-issues--todos)
11. [Odoo Update Risk Register](#11-odoo-update-risk-register)
12. [Developer Runbook](#12-developer-runbook)

---

## 1. Overview

`gl_custom_module` extends Odoo's native **Planning** app for GL-Ecologie's specific operational needs. It has two largely independent feature areas:

- **Employee Availability & Shift Planning** — a workflow-based system where employees self-declare per-day availability per shift type, managers validate them, and the planning scheduler enforces those declarations (plus several other constraints) when assigning employees to shifts.
- **Materials Management** — a lightweight inventory catalogue (material types, units, statuses, consumables) linked to planning shifts.

---

## 2. Repository Layout

```
odoo-sh/
├── custom-addons/
│   └── gl_custom_module/
│       ├── __manifest__.py
│       ├── __init__.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── planning_shift_type.py
│       │   ├── planning_slot.py                              ← inherits planning.slot
│       │   ├── planning_employee_availability.py
│       │   ├── planning_employee_availability_batch_edit_wizard.py
│       │   ├── planning_employee_availability_calendar_resource.py
│       │   ├── hr_employee.py                                ← inherits hr.employee
│       │   ├── hr_employee_public.py                         ← inherits hr.employee.public
│       │   ├── materials_consumable_type.py
│       │   ├── materials_material_category.py
│       │   ├── materials_material_type.py
│       │   ├── materials_material_unit.py
│       │   └── materials_material_unit_status.py
│       ├── views/
│       │   ├── planning_slot_views.xml
│       │   ├── planning_shift_type_views.xml
│       │   ├── planning_employee_availability_views.xml
│       │   ├── planning_employee_availability_batch_edit_wizard_views.xml
│       │   ├── hr_employee_views.xml
│       │   ├── hr_employee_public_views.xml
│       │   ├── materials_*.xml  (5 files)
│       │   └── materials_menu_views.xml
│       ├── security/
│       │   ├── security.xml          ← record rules
│       │   └── ir.model.access.csv   ← ACL
│       └── static/src/
│           ├── views/employee_availability_calendar/
│           │   ├── employee_availability_calendar_view.js
│           │   └── employee_availability_calendar.xml
│           └── scss/
│               └── employee_availability_calendar.scss
└── docs/
    └── handover.md  ← this file
```

---

## 3. Module Dependencies

| Odoo App | Why needed |
|---|---|
| `base` | res.users, resource.resource |
| `planning` | planning.slot, planning.role, group_planning_manager/user |
| `hr` | hr.employee, hr.employee.public |
| `project` | Declared but not actively used in current code |

> **Note:** `project` is listed as a dependency in `__manifest__.py` but no model or view currently references it. It may be a legacy or planned dependency — verify before removing.

---

## 4. Feature Areas

### 4.1 Employee Availability & Shift Planning

**Flow:**

```
Employee creates availability entry
        │  (auto-triggers on create)
        ▼
  state: draft → validation_requested
        │  (manager reviews activity)
        ▼
  state: validated  ←──────────────────── manager calls action_validate
        │
        ▼
  Shift assignment (planning.slot):
    6 constraints checked on create/write:
      1. Weekly max shifts
      2. Shift-type preference
      3. Planning role match
      4. No evening→morning same employee
      5. Weekend availability
      6. Validated availability entry exists
```

**Key UX surfaces:**
- `Planning > Employee Availability > Availability by resource` — manager view, all resources
- `Planning > Employee Availability > My availability` — self-service view filtered to current user
- Custom calendar view with colour-coded entries (see §8)
- Batch edit wizard available as server action on list/calendar selection

### 4.2 Materials Management

Lightweight catalogue under `Planning > Materials`. No automation or constraints yet — all quantities (`booked_quantity`, `needed_stock`) are manually maintained integers.

**Hierarchy:**
```
materials.material_category
  └─ materials.material_type  (uses materials.consumable_type)
       └─ materials.material_unit  (has materials.material_unit_status)
```

Materials are linked to shifts via `planning.slot.material_type_ids` (Many2many).

---

## 5. Custom Models

### `planning.shift_type`

**File:** `models/planning_shift_type.py`

Simple lookup table. Name and a short `code` (e.g. "morning", "afternoon"). Used as a foreign key throughout the availability and slot systems.

> **Critical:** The evening/morning conflict detection in `planning.slot` uses **string matching on `name`** (`.endswith("vening")` / `.endswith("orning")`), not the `code` field. Shift type names must therefore end in the Dutch/English suffix for this logic to work. See §10.

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Required |
| `code` | Char | Required, e.g. "morning" |

---

### `planning.employee_availability_entry`

**File:** `models/planning_employee_availability.py`

Core availability model. One record = one employee's availability for one date and one shift type.

| Field | Type | Notes |
|---|---|---|
| `resource_id` | Many2one `resource.resource` | Required, cascades on delete, indexed. Defaults to current user's resource. |
| `date` | Date | Required, indexed |
| `shift_type_id` | Many2one `planning.shift_type` | Required, restricted on delete |
| `available` | Boolean | Default False |
| `state` | Selection | draft / validation_requested / validated |
| `notes` | Char | Free text |
| `name` | Char (computed) | Stores `shift_type.name`; stored=True |
| `style_key` | Char (computed) | CSS class suffix; not stored |

**SQL constraint:** `UNIQUE(resource_id, date, shift_type_id)` — one entry per employee/date/shift combination.

**Mixins:** `mail.thread`, `mail.activity.mixin` — full chatter and activity support.

**State transitions:**

| Action | Who | From | To |
|---|---|---|---|
| `create()` | Anyone | — | draft → auto-triggers request validation |
| `write()` | Anyone | any | resets to draft + re-triggers request validation if a meaningful field changed |
| `action_request_validation` | Anyone | draft, validated | validation_requested |
| `action_validate` | Planning Manager only | validation_requested | validated |
| `action_reset_to_draft` | Planning Manager only | validation_requested, validated | draft |

**`write()` override:** if any of `available`, `date`, `shift_type_id`, or `notes` is in the write payload, the record is reset to `draft` (if not already) and `action_request_validation()` is called. A context flag `_skip_revalidation=True` prevents the reset-state write from re-triggering the loop.

On `action_request_validation`: groups entries by manager and creates one `mail.mail_activity_data_todo` activity per manager (not per entry), with a note stating the entry count and earliest–latest date range. Deadline is 3 days from today.

On `action_validate`: sends a real-time `bus.bus` `simple_notification` toast to the affected employee (one per batch), and a persistent inbox `message_notify` to the same partner. No To-Do activity is created.

On `action_reset_to_draft`: same pattern as `action_validate` — bus toast + inbox message to the affected employee.

**`_compute_style_key` mapping:**

| state | available | style_key |
|---|---|---|
| draft | any | `draft` |
| validation_requested | True | `validation_requested_yes` |
| validation_requested | False | `validation_requested_no` |
| validated | True | `validated_yes` |
| validated | False | `validated_no` |

---

### `planning.employee_availability_calendar_resource`

**File:** `models/planning_employee_availability_calendar_resource.py`

Stores per-user sidebar filter state for the availability calendar (which resources are checked/visible). Odoo's built-in calendar filter mechanism (`write_model`/`write_field`/`filter_field` attributes on `<field>` in calendar view) populates this automatically.

Key method: `get_calendar_filters(user_id, field_names)` — auto-creates missing records for all active employees (managers) or just the current employee (regular users), then returns the list.

| Field | Type | Notes |
|---|---|---|
| `user_id` | Many2one `res.users` | Required, cascades |
| `resource_id` | Many2one `resource.resource` | The resource being filtered |
| `active` | Boolean | |
| `checked` | Boolean | Whether resource is shown in calendar |

---

### `planning.employee_availability_batch_edit_wizard`

**File:** `models/planning_employee_availability_batch_edit_wizard.py`

TransientModel wizard to bulk-update `shift_type_id` and/or `available` on selected availability entries. Triggered as a server action from the list/calendar view.

After applying changes, automatically calls `action_request_validation()` on all modified entries.

> **Known bug:** There is a **syntax error** on the `entry_ids` Many2many field definition — a comma is missing between `relation=` and `string=` arguments. The module will fail to load until this is fixed. See §10.

---

### `materials.consumable_type`

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Required |
| `material_type_ids` | One2many → `materials.material_type` | |
| `current_stock` | Integer | Manually maintained |
| `needed_stock` | Integer | Manually maintained (not computed) |
| `notes` | Char | |

---

### `materials.material_category`

Simple grouping for material types.

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Required |
| `material_type_ids` | One2many → `materials.material_type` | |
| `notes` | Char | |

---

### `materials.material_type`

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Required |
| `material_category_id` | Many2one → `materials.material_category` | |
| `material_unit_ids` | One2many → `materials.material_unit` | |
| `booked_quantity` | Integer | Manually maintained |
| `available_quantity` | Integer (computed) | `len(material_unit_ids) - booked_quantity` |
| `consumable_type_id` | Many2one → `materials.consumable_type` | |
| `consumable_quantity` | Integer | |
| `notes` | Char | |

---

### `materials.material_unit`

Individual physical unit of a material type.

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Required |
| `material_type_id` | Many2one → `materials.material_type` | |
| `material_status_id` | Many2one → `materials.material_unit_status` | |
| `serial_number` | Char | |
| `rental` | Boolean | |
| `notes` | Char | |

---

### `materials.material_unit_status`

Lookup table for unit statuses (e.g. "In service", "Broken", "In repair").

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Required |
| `material_unit_ids` | One2many → `materials.material_unit` | |
| `notes` | Char | |

---

## 6. Inherited Models

### `planning.slot` (extends `planning.slot`)

**File:** `models/planning_slot.py`

Added fields:

| Field | Type | Notes |
|---|---|---|
| `task_id` | Many2one `project.task` | Links shift to a task; domain filtered by `project_id`. Replaced old Studio field `x_studio_task` (fully deleted). |
| `shift_type_id` | Many2one `planning.shift_type` | Optional; used in constraint checks |
| `counts_for_max_shift_per_week` | Boolean | Default True; flag individual shifts as exempt |
| `material_type_ids` | Many2many `materials.material_type` | Materials required for this shift |
| `resource_ids_domain` | Binary (computed) | Dynamic domain for `resource_id` dropdown |
| `can_register_hours` | Boolean (computed) | True if current user is a planning manager or the assigned employee. Controls "Register Hours" button visibility. |
| `date_outside_protocol_window` | Boolean (computed, store=False) | True when shift date falls outside the protocol visit window defined by `task_id.x_studio_protocol_visit_single`. Shown as a non-blocking amber alert in the form. |

**`_compute_resource_domain`:**
Runs on every slot form load/change of `start_datetime`, `shift_type_id`, `role_id`, or `counts_for_max_shift_per_week`. Iterates over **all active employees** with `max_shifts_per_week >= 0` and filters out those who:
- Don't have the slot's role in their `planning_role_ids`
- Don't have the slot's shift type in their `allowed_shift_type_ids`
- Have an availability conflict, evening/morning conflict, or weekend conflict
- Would exceed their weekly max shift count

> **Performance warning:** This method runs `search_count` for each candidate employee per slot. On a large employee base this can be slow. See §10.

**Constraint enforcement (on `create` and `write`):**
All 6 checks are enforced server-side as `ValidationError`. The domain computation is a UI hint only — the constraints are the actual gate.

**Evening/morning conflict logic** (`_check_evening_morning_shift_conflict`):
- If shift name ends in `"vening"` → checks that the same resource has no shift ending in `"orning"` the following day
- If shift name ends in `"orning"` → checks that the same resource has no shift ending in `"vening"` the previous day
- Only applies when `employee.combine_evening_morning_shift == False`

**Weekend conflict logic** (`_check_employee_works_weekends_conflict`):
Weekend is defined broadly:
- Saturday (isoweekday=6) or Sunday (isoweekday=7)
- Friday evening (isoweekday=5 + name ends in "vening")
- Monday morning (isoweekday=1 + name ends in "orning")

---

### `hr.employee` (extends `hr.employee`)

**File:** `models/hr_employee.py`

Added fields:

| Field | Type | Notes |
|---|---|---|
| `allowed_shift_type_ids` | Many2many `planning.shift_type` | Relation table: `hr_employee_shift_type_rel` |
| `max_shifts_per_week` | Integer | 0 = no limit |
| `available_to_work_weekends` | Boolean | |
| `combine_evening_morning_shift` | Boolean | |

Also restricts three existing fields to `hr.group_hr_user` (HR managers only):
- `version_id`
- `exceptional_location_id`
- `planning_role_ids`

> These fields (`version_id`, `exceptional_location_id`) are not standard Odoo fields — they are likely added by another module or Studio. If that module is ever removed, this will cause a startup error.

---

### `hr.employee.public` (extends `hr.employee.public`)

**File:** `models/hr_employee_public.py`

Exposes the same 4 planning preference fields as writable related fields via `related_sudo=True`. This allows employees to self-manage their own preferences through the public employee profile without needing `hr.group_hr_user` access.

> **Security consideration:** `related_sudo=True` means writes bypass `hr.employee` access checks. An employee can change their own planning preferences even without HR rights — this is intentional but should be reviewed if access policies change.

---

## 7. Security Model

### Access Control List (`ir.model.access.csv`)

| Model | Manager | Regular User |
|---|---|---|
| `planning.shift_type` | CRUD | R only |
| `planning.employee_availability_entry` | CRUD | CRW (no delete) |
| `planning.employee_availability_calendar_resource` | CRUD | RW (no create/delete) |
| `planning.employee_availability_batch_edit_wizard` | CRUD | CRUD (TransientModel, ephemeral) |
| `materials.consumable_type` | CRUD | R only |
| `materials.material_category` | CRUD | R only |
| `materials.material_type` | CRUD | R only |
| `materials.material_unit` | CRUD | R only |
| `materials.material_unit_status` | CRUD | R only |

> ACL entries exist for all custom models including the TransientModel wizard.

### Record Rules (`security/security.xml`)

| Rule | Group | Domain |
|---|---|---|
| Employee availability: users see own entries | `base.group_user` | `resource_id.user_id = current user` |
| Employee availability: managers see all entries | `planning.group_planning_manager` | `(1=1)` — no filter |

The manager rule overrides the user rule (Odoo applies the most permissive matching rule).

---

## 8. Frontend (OWL / JS / SCSS)

### Custom Calendar View: `employee_availability_calendar`

**Registered as:** `registry.category("views").add("employee_availability_calendar", ...)`

**Used in:** both calendar views for `planning.employee_availability_entry` via `js_class="employee_availability_calendar"`.

**Architecture:**

```
employeeAvailabilityCalendarView
├── Controller: EmployeeAvailabilityCalendarController
│     extends CalendarController
│     static template = "gl_custom_module.EmployeeAvailabilityCalendarController"
│     adds: AvailabilityLegend component
│     adds: setup() — orm, action, user services; isManager check via onWillStart
│     adds: selectedIds getter (from model.selectedRecords Set)
│     adds: onBatchEdit(), onBatchValidate(), onBatchResetToDraft() handlers
└── Renderer: EmployeeAvailabilityCalendarRenderer
      extends CalendarRenderer
      overrides: day/week/month sub-renderers with:
        EmployeeAvailabilityCalendarCommonRenderer
          extends CalendarCommonRenderer
          overrides: eventClassNames() → appends o_availability_event +
                     o_availability_event_title + o_availability_{style_key}
```

**OWL Templates** (`employee_availability_calendar.xml`):

- **`gl_custom_module.EmployeeAvailabilityCalendarController`** — `t-inherit="web.CalendarController"` with `t-inherit-mode="primary"`. Creates a new named template (does NOT patch the parent globally). Injects Edit / Validate / Reset to Draft buttons into the multi-selection bar, visible only when `nbSelected > 0`. Validate and Reset buttons additionally gated by `isManager`.
- **Legend** — extends `web.CalendarSidePanel` via `t-inherit-mode="extension"`. Injects legend block inside `.o_calendar_sidebar`. Intentionally global (extension mode) since it is always wanted for this view.

> **`t-inherit-mode` distinction:** `"primary"` creates an independent named template the component can reference via `static template`; `"extension"` patches the parent in-place and does NOT register a new name. Using `"extension"` for the controller template causes `OwlError: Missing template`.

**SCSS classes** (`employee_availability_calendar.scss`):

| CSS class | Applied to | Visual | Meaning |
|---|---|---|---|
| `.o_availability_event` | Outer event element | No border-radius, 1px solid border, larger font, 2px vertical padding | All availability events |
| `.o_availability_event_title` | Outer event element | — | Marker class; targets `.o_event_title` descendant for text styling |
| `.o_availability_event_title .o_event_title` | Inner title div | White semi-transparent background, rounded, centred, dark forced text | Readable text over gradient backgrounds |
| `.o_availability_draft` | Outer event element | Diagonal grey stripes | Draft entry |
| `.o_availability_validation_requested_yes` | Outer event element | Diagonal green stripes | Pending validation, available |
| `.o_availability_validation_requested_no` | Outer event element | Diagonal red stripes | Pending validation, not available |
| `.o_availability_validated_yes` | Outer event element | Solid green `#81c784` | Confirmed available |
| `.o_availability_validated_no` | Outer event element | Solid red `#ef9a9a` | Confirmed unavailable |

> `style_key` is a computed (non-stored) field on the model. The calendar view fetches it by listing `<field name="style_key"/>` in the calendar view XML. Ensure this field remains in the `<calendar>` fields list if the view XML is ever refactored.

---

## 9. Key Architectural Decisions

### A. Strict availability mode
`_check_employee_availability_conflict` returns `True` (conflict = block) when **no validated entry is found** for a resource/date/shift combination. This means the absence of an entry is treated as unavailable. Employees must proactively declare and have their availability validated before they can be assigned to any shift.

### B. Availability via `resource.resource`, not `hr.employee`
The availability entry model stores `resource_id` (Many2one `resource.resource`) rather than `employee_id`. This aligns with how `planning.slot` stores assignments and avoids joining through `hr.employee`. The tradeoff is that you must traverse `resource_id.employee_id` to get employee preferences and `resource_id.user_id` to find the linked user.

### C. Employee self-service via `hr.employee.public`
Rather than granting employees HR manager rights to edit their own records, the module uses `hr.employee.public` with `related_sudo=True`. This is the standard Odoo pattern for employee self-service and avoids privilege escalation.

### D. Dynamic resource domain as UI hint only
`resource_ids_domain` is a computed Binary field that restricts the dropdown in the shift form. It is **advisory only** — the actual enforcement is in `_check_planning_constraints()` (called on create/write). This dual-layer approach prevents confusing UX (empty dropdown) while still blocking invalid assignments.

### F. `write()` override forces re-validation on meaningful field changes

Any write to `available`, `date`, `shift_type_id`, or `notes` automatically resets the entry to `draft` and triggers `action_request_validation()`, regardless of who performs the write (employee or manager). This ensures availability changes never go silently unnoticed. A `_skip_revalidation` context flag prevents the internal state-reset write from looping.

### E. Materials is a standalone catalogue
The materials sub-system has no business logic or automation. `booked_quantity` and `needed_stock` are plain integers requiring manual updates. The link to planning shifts (`material_type_ids` on `planning.slot`) is for informational purposes only — no stock deduction or validation is implemented.

---

## 10. Known Issues & TODOs

### Fragile: Shift type name string matching

Evening/morning conflict detection and weekend detection both rely on `.endswith("vening")` and `.endswith("orning")`. This is a naming convention constraint — if shift types are renamed or translated, the logic silently breaks with no error.

**Recommendation:** Use the `code` field on `planning.shift_type` for this logic instead, e.g. `code in ("morning", "evening")`.

---

### Performance: N+1 queries in `_compute_resource_domain`

For each slot, the method iterates over every candidate employee and runs `search_count` per candidate. With 50 employees this is 50 DB queries per slot form open. Consider a single grouped query.

---

### `booked_quantity` / `needed_stock` are manual integers

`materials.material_type.booked_quantity` and `materials.consumable_type.needed_stock` are not computed — they need to be updated by hand. There is an existing `# TODO: Remove conditional material assignment` comment in `planning_slot.py` suggesting this was intended to be automated.

---

### `hr.employee` references possibly non-standard fields

`models/hr_employee.py` restricts `version_id` and `exceptional_location_id` to `hr.group_hr_user`. These are not standard Odoo fields. They may come from Studio or another custom module. If that module is removed, Odoo will error on startup with `FieldDoesNotExist`.

---

### `project` dependency is actively used

`project` is in `depends` for both `gl_custom_module` and `studio_customization`. It is used via:
- `planning.slot.task_id` — Many2one to `project.task`
- `project.task.x_studio_assigned_shifts` — Studio one2many showing shifts per task
- Various Studio view customizations on `project.task` and `project.project`

---

### Gantt form view references a Studio action

`views/planning_slot_views.xml` inherits `planning.planning_view_form_in_gantt` and references action `studio_customization.request_assignment_7a79e11f-811d-41cc-b72b-7346e4636a2f`. If the Odoo Studio customizations are removed or the database is restored without them, this view will fail to render.

---

## 11. Odoo Update Risk Register

This section covers everything likely to break if Odoo core or the `planning`/`hr` apps are updated.

### High risk

| Item | Risk | Why |
|---|---|---|
| `CalendarCommonRenderer.eventClassNames` | **High** | The JS override calls `super.eventClassNames(params)` and accesses `this.props.model.records[params.event.id]`. The internal data structure of the calendar model (`records`, `rawRecord`) has changed between major versions and may change again. |
| `web.CalendarSidePanel` XML template | **High** | The legend is injected via `t-inherit` XPath into `//div[hasclass('o_calendar_sidebar')]`. If Odoo renames or restructures the sidebar, the legend will disappear silently. |
| `planning.planning_view_form` and `planning.planning_view_form_in_gantt` | **High** | Both form view XMLs are inherited. If Odoo renames the group `slot_info_right`, removes the `action_self_assign` button, or restructures the form layout, the XPaths will fail and the upgrade will abort. |

### Medium risk

| Item | Risk | Why |
|---|---|---|
| `hr.view_employee_form` XPath on `page[@name='work_information']` | **Medium** | If Odoo renames the page or moves the planning group inside it, the custom fields won't appear. The module will still install. |
| `planning.group_planning_manager` external ID | **Medium** | Used as a security group reference throughout. If Odoo ever renames this group, all permission checks and record rules break. |
| `resource_id.employee_id` reverse relation | **Medium** | `planning.slot` and availability checks traverse `resource_id.employee_id`. This is a standard Odoo relation but the direction of navigation (`resource.resource` → `hr.employee`) relies on `hr.employee` adding `resource_id` field, which could change. |
| `hr.hr_employee_public_view_form` XPath | **Medium** | Same risk as the employee form view. |

### Low risk

| Item | Risk | Why |
|---|---|---|
| `mail.mail_activity_data_todo` data ref | **Low** | Standard Odoo activity type. Unlikely to change. |
| `planning.planning_menu_root` / `planning.planning_menu_settings` menu refs | **Low** | Menu structure is relatively stable but can shift between versions. |
| `planning.planning_slot` `_inherit` | **Low** | Core inheritance pattern. No risk from the pattern itself, but any field renamed on `planning.slot` (e.g. `resource_id`, `start_datetime`, `role_id`) will break the extension. |

---

## 12. Developer Runbook

### Setting up the pre-commit hook (new developer setup)

A pre-commit hook at `.githooks/pre-commit` automatically bumps the module patch version whenever any file under `custom-addons/gl_custom_module/` is staged. This triggers Odoo.sh to auto-upgrade the module on push.

Each developer must enable it once after cloning:

```bash
git config core.hooksPath .githooks
```

This is a local git config — it is not committed to the repo and must be set per machine.

---

### Installing the module

```bash
# From the Odoo shell or via the UI
odoo -d <db> -i gl_custom_module
```

Or via Odoo.sh: push to the branch. If the pre-commit hook is active, the version will have been bumped automatically and Odoo.sh will pick up the upgrade on the next push. Otherwise, manually upgrade from Apps.

### Upgrading the module after code changes

```bash
odoo -d <db> -u gl_custom_module
```

> Always run an upgrade (not just restart) when changing model fields, security files, or view XML.

### Adding a new shift type

1. Go to `Planning > Configuration > Shift Types`
2. Create the record with a unique `name` and `code`

> **Important:** If the shift type should participate in evening/morning conflict detection, the `name` must end with `"vening"` (evening) or `"orning"` (morning). Until the fragile string matching is replaced with `code`-based logic, this is a hard requirement.

### Adding a new employee preference constraint

1. Add the field to `hr.employee` in `models/hr_employee.py`
2. Add a matching writable related field to `hr.employee.public` in `models/hr_employee_public.py`
3. Add the UI field to `views/hr_employee_views.xml` (inside the Planning group)
4. Add the UI field to `views/hr_employee_public_views.xml`
5. Add the constraint check to `planning.slot._check_planning_constraints()`
6. Add the domain filter to `planning.slot._compute_resource_domain()` for the UI hint

### Modifying the availability calendar colours

Edit `static/src/scss/employee_availability_calendar.scss`. The CSS classes follow the pattern `.o_availability_{style_key}`. The `style_key` values are computed in `PlanningEmployeeAvailabilityEntry._compute_style_key()`.

After editing SCSS, the asset bundle must be regenerated:
- In development: `?debug=assets` in the URL and a browser hard-refresh
- In production: `odoo -d <db> -u gl_custom_module` or clear assets via Settings > Technical > User Interface > Assets

### Checking the availability workflow in a new database

1. Create an employee and link them to a user
2. Assign shift types to the employee (`allowed_shift_type_ids`)
3. Log in as the employee, go to `My Availability`, create an entry
4. Log in as a Planning Manager, validate the entry
5. Create a `planning.slot` with a matching date/shift type — the employee should be selectable

---

### Studio customization workflow

The `studio_customization` module contains Odoo Studio-generated field and view definitions alongside hand-edited fixes. Follow this order when making Studio changes:

1. Make the change in **production** via the Studio UI
2. Export Studio customizations from production (Settings → Technical → Studio → Export)
3. Review the diff — accept changes to `ir_ui_view.xml` and `ir_model_fields.xml`; reject anything unexpected
4. Commit and push to the development branch; test on staging before deploying back to production

**Critical rules:**
- All Studio view `ir.model.data` records must have `noupdate=False`. If they are `True`, code-side XML changes are silently ignored on upgrade. Check via Settings → Technical → External Identifiers, filter by module=`studio_customization`.
- If a field has an `ir.model.data` entry registered to `studio_customization` but **no `<record>`** in `ir_model_fields.xml`, Odoo will **auto-delete the field** on the next module upgrade (including dropping the DB column). Always ensure exported fields have matching XML records.
- When deleting a Studio field, the order matters: (1) remove all view references via Studio UI, (2) delete any dependent fields (e.g. one2many fields that use it as `relation_field`), (3) delete the field itself.

---

*Document generated from source analysis of commit range on branch `custom_planning_module`.*
