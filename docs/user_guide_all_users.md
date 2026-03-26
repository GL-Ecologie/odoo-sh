# GL-Ecologie — Odoo Planning System: User Guide

**Version:** 1.2
**Last updated:** 2026-03-26
**Prepared by:** Ruiz Burgos Ecology and Software

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Getting Started](#2-getting-started)
3. [For All Users](#3-for-all-users)
   - 3.1 [General features across apps](#31-general-features-across-apps)
   - 3.2 [Your Employee Profile](#32-your-employee-profile)
   - 3.3 [Filling In Your Availability](#33-filling-in-your-availability)
   - 3.4 [Viewing Your Schedule and Open Shifts](#34-viewing-your-schedule-and-open-shifts)
   - 3.5 [Requesting an Open Shift](#35-requesting-an-open-shift)
   - 3.6 [Registering Hours](#36-registering-hours)
   - 3.7 [Viewing Your Timesheets](#37-viewing-your-timesheets)
   - 3.8 [Viewing Locations](#38-viewing-locations)
   - 3.9 [Viewing Protocols, Protocol Visits and Species](#39-viewing-protocols-protocol-visits-and-species)
   - 3.10 [Viewing Projects and Tasks](#310-viewing-project-and-tasks)
4. [Inventory & Tools](#4-inventory--tools)
5. [Notifications & Approvals](#5-notifications--approvals)

---

## 1. Introduction



This guide covers the day-to-day use of the GL-Ecologie planning system implemented using the Odoo platform. **Only non-manager related information is described in this document**. Manager-related documentation will follow at a future time.

If you are new to the system, start with §2 (Getting Started) and then follow the track that matches your role.

---

## 2. Getting Started

### Accessing the system

The system is available at: [**https://gl-ecologie.odoo.com/odoo**](https://gl-ecologie.odoo.com/odoo)

Log in with the email address and password defined when your account was created (either provided by your manager or specified by you). If you have forgotten your password, click *Reset password* on the login page and follow the instructions sent to your email.

### Navigating the main menu

After logging in you will see the main application menu at the top of the screen. The apps you will use most often are:

| App | Used for |
|-----|----------|
| **Employees** | Your employee profile |
| **Planning** | Shifts, availability, your schedule |
| **Project** | Projects, tasks |
| **Protocols** | Protocols, protocol visits and species|
| **Timesheets** | Timesheets tracking |
| **Approvals** | Approval requests status, validation and tracking |

Administrators also have access to the **Settings** app, where system configuration is handled.

<p align="center">
  <img src="gallery/homepage_no_admin.png" alt="Home page for non administrator users" />
</p>
<center><i> Home page for non administrator users </i></center>


### Language

The system supports limited automatic translation of the platform to multiple languages. Dutch and English are currently supported. 

If you would like the platform language changed, please contact your manager or platform administrator.
If you are a manager/administrator, you can chage the language for a specific user at:

*Settings* → *Users & Companies* → *Users* → (the desired user) → *Preferences* → *Language* 

### Mobile use

The system works on mobile browsers. For the best experience when checking your schedule or registering hours on the go, use the Planning app in list or calendar view. The availability calendar works best on a desktop.

In addition, Odoo has a mobile phone apps available for both [*Android*](https://play.google.com/store/apps/details?id=com.odoo.mobile) and [*iOS*](https://apps.apple.com/app/odoo/id1272543640)

---

## 3. For All Users

### 3.1 General features across apps

#### Menus
A menu bar is displayed at the top of each application page. Each menu option will either redirect to a page or will display a sub-menu list, which when clicked will redirect to its assigned page.
<br>
<p align="center">
  <img src="gallery/general_features_menu bar.png" alt="Menu bar" />
</p>
<center><i> Menu bar for the Planning app (as a non admin user) </i></center>
<br>

#### Views
The platform offers multiple types of ways to visualize information at a given page, called views. The most common views are ***Form***, ***List***, ***Gantt***, ***Pivot*** and ***Calendar***. Which views are available at a given time depend on the specific page. Furthermore, different views will offer different features/operations.

You can pick which view you want by clicking on the respective icon displayed at the top-right of the window:
<br>
<p align="center">
  <img src="gallery/general_features_views_icons.png" alt="View icons" />
</p>
<center><i> View icon section of form. Click one will switch to that view. </i></center>
<br>

#### Saving changes on current entry/form
When adding or editing single entries -availability, shifts, tasks, etc.-, **changes are automatically saved if you leave that page**. In addition, ***Save*** and ***Discard*** small buttons will appear on the top left section, underneath the menu bar (often next to other Buttons.), a **cloud shaped button** for the former and an **x shaped button** for the latter.

<br>
<p align="center">
   <img src="gallery/employee_availability_add_entry_list_view_save_button.png" alt="Save and discard buttons for single entry" />
</p>
<center><i>Save and discard buttons for single entry</i></center>
<br>

#### Searching, filtering and grouping entries
Many views (List, Gantt, Calendar...) display a search bar at the top center of the page. This bar allows to search for entries (records), filter and/or group them following specific criteria. For instance, it's possible to show only the availability entries for a specific resource, or to group shifts by a project and task. These are just two examples of what is possible.

<br>
<p align="center">
   <img src="gallery/general_features_search_bar.png" alt="Search bar" />
</p>
<center><i>Search, filter and/or group entries</i></center>
<br>

<br>
<p align="center">
   <img src="gallery/general_features_search_bar_grouping_example.png" alt="Shifts grouped by project and task" />
</p>
<center><i>Example: Planning schedule grouped by project and task</i></center>
<br>

#### Action buttons
Besides the intuitive buttons visible throughout the platform, there are a *category* of buttons, the so called ***Actions buttons*** which are either easy to miss, or only become visible under certain circumstances: for instance when a record is selected ***List*** **view**. You can identify them by their icon (a toothed wheel or gearwheel), sometimes accompanied by the word ***Actions***.

These buttons offer different functionalities, like exporting/importing records, deleting selected records, etc. 


<br>
<p align="center">
   <img src="gallery/general_features_actions_buttons.png" alt="Icon only actions button" />
</p>
<center><i>Actions button, icon only. Often shows importing/exporting options.</i></center>
<br>

<br>
<p align="center">
   <img src="gallery/general_features_actions_buttons_with_label.png" alt="Icon and label actions button" />
</p>
<center><i>Actions button, icon and label, with multiple options</i></center>
<br>

### 3.2 Your Employee Profile

Your employee profile **stores your personal preferences** that the planning system uses when assigning shifts. **This profile can only be edited by managers or system administrators.** If you want to have your employee profile updated (for instance if your maximum number of shifts per week changed, or you got access to a vehicle) please notify your manager or system administrator and they will update your profile.

You can find your profile at ***Employees*** → (your name).

The following information is available:

| Tab | Information |
|-------|---------------|
| **All** | Employee name, email address, contact phone numbers |
|**Work** | Department job title, manager, office location, work location, planning constraints -maximum shifts per week, allowed shift types, weekend availability and willingness to combine evening and morning shifts.)|
| **Resume** | Work experience, skills & certifications |
|**Certifications** | Employee certifications |

<br>

> **Important!**
>
> Non manager/administrator employees can only see their own profile.

---

### 3.3 Filling In Your Availability

Before a manager can assign you to a shift, you must declare your availability and have it **validated**. This is the most important step in the planning workflow.

#### How availability works

The system operates in **strict mode**: if there is no validated availability entry for a given date and shift type, you are treated as unavailable — even if you are free that day. You must proactively declare availability for every date and shift type you are willing to work.

#### Step-by-step

1. Go to **Planning → Employee Availability → My Availability**
2. Two views are available: Calendar (default) or List:
   - **Calendar** view:
      1. Select on **one or multiple days** (control + click to select multiple non-consecutive days, shift + click to select all days in a specific range or simply click and drag across calendar days)
      2. Click on the ***Add*** button that will appear on top of the Calendar, **next to the *N selected*** **information box.**
      3. Fill in:
         - **Shift type**: the type of shift you are/are not available for (morning, evening, etc.)
         - **Available**: check this box if you *are* available; leave unchecked if you want to declare that you are *not* available for that day/shift
      4. Press ***Add***
   - **List** view:
      1. Press the ***New*** button at the top left of the screen.
      2. Fill in:
         - **Date**: the date you want to specify availability for.
         - **Shift type**: the type of shift you are/are not available for (morning, evening, etc.)
         - **Available**: check this box if you ***are*** available; leave unchecked if you want to declare that you are ***not*** available for that day/shift
         - **Notes**: Any extra information the manager should know.
      3. Press on the cloud shaped save button to save, or the cross button to discard.

<br>
<p align="center">
   <img src="gallery/employee_availability_add_entry_list_view_save_button.png" alt="Save button for employee availability entry in list mode" />
</p>
<center><i>New employee availability entry in list mode - Save button</i></center>
<br>

> **New availability entries are automatically sent for validation**.

> You need **one entry per date per shift type**. If you are available for both a morning and an evening on the same day, create two separate entries.

#### What happens next?

After you save, the entry status changes to **Validation Requested** and your manager receives a to-do notification. Once the manager validates it, you will receive a confirmation notification and the entry will turn solid green (confirmed available) in your calendar or solid red (confirmed not available).
Alternatively, the manager might decide to deny the validation request. In this case your entry/ies will be sent back to ***Draft*** state. You can then adjust them and send them again for validation.

#### Viewing your availability calendar

The calendar view shows all your entries colour-coded by status:

| Colour | Meaning |
|--------|---------|
| Grey stripes | Draft — not yet submitted |
| Green stripes | Submitted, waiting for validation |
| Red stripes | Submitted unavailable, waiting for validation |
| Solid green | Validated — available |
| Solid red | Validated — not available |

> **If your availability changes** after it has been validated, edit the entry (change the date, shift type, or available flag). It will automatically reset to *Validation Requested* and your manager will be notified again.

Clicking on an entry will display a popup form with the details of that entry. You can also edit the entry by click the ***Edit*** button at its foot.

#### Editing your availability

Availability can be edited one **single entry at a time by clicking on a specific entry** or by selecting **multiple entries at a time** (batch editing), the two options availble in both list an calendar view).

The steps to batch editing are as follow, depending on the view:
   - **Calendar** view:
      1. Select on **one or multiple days** which contain existing entries (same procedure as for creating)
      2. Click on the ***Edit*** button that will appear on top of the Calendar, **next to the *N selected*** **information box.** 
      3. Select which field you would like to edit:
         - **Update Shift type**: If checked, it will display the ***Shift type*** field so you can edit it.
         - **Update availability**: If checked, it will display the ***Available*** field so you can edit it.
      4. Press ***Apply*** or ***Discard*** to accept or discard the changes.
   - **List** view:
      1. Select the entries you want to edit.
      2. An ***Actions*** button will appear on top of the Calendar, **next to the *N selected*** **information box.**. Press on ***Actions*** → ***Batch edit availability***
      3. Select which field you would like to edit:
         - **Update Shift type**: If checked, it will display the ***Shift type*** field so you can edit it.
         - **Update availability**: If checked, it will display the ***Available*** field so you can edit it.
      4. Press ***Apply*** or ***Discard*** to accept or discard the changes.

<br>

> **Edited availability entries are automatically sent for validation**.

---

### 3.4 Viewing Your Schedule and Open Shifts

Go to **Planning → My Planning** to see all shifts you are assigned to, and any open shifts available (shifts that have been created and published by a manager but do not yet have an assigned resource).
The default view is a ***Gantt***, displayed **weekly**. If you want to see a different time split you can change that by either selecting a different time window (monthly, quarterly, yearly...) on the top left. Alternatively you can select a different view, like **Calendar** (that defaults to monthly).

Clicking on a specific shift will allow you to view that shift information (by clicking on the ***View*** button).

<br>
<p align="center">
   <img src="gallery/planning_view_mine_open_gantt.png" alt="My planning - Gantt view" />
</p>
<center><i>My weekly schedule as shown by the Gantt view. Clicking on a specific shift shows a short description popup.</i></center>
<br>

Each shift form shows the most relevant information you need for that shift:
| Field | Description | Sample values|
|---|---|---|
|***Resource*** | Who is assigned to this shift. Empty in the case of Open shifts. | *Joost van NotMyTrueName*, *John Doe* |
|***Role*** | What role this shift is for. | *Fieldworker*, *Project leader* |
|***Project*** | What project -if any- this shift is associated with. | *Top Secret project 001: Invade Greenland* |
|***Task*** | What task of the specified project -if any- this shift is associated with | *Task 01: Negotiate assistance with Donald T.* |
|***Shift type***| Shift type associated to this shift | *Hangover morning (16:00-18:00)*, *Borrel evening (16:00-18:00)*|
|***Date***| Date and time of this shift | *Mar 26, 16:00 → Mar 26m 18:00*|
|***Allocated time*** | Length of the shift in *hours:minutes* | 02:00 |
|***Counts for max shift per week?***| Whether this shift should take into account employee's maximum  shift per week constraint | *Yes*, *No* |
|***Required Materials***| Which material types are needed for this shift? | *Batlogger*, *Camera Trap*, *USS Gerald R. Ford* |
|***Reminder***| Optional preparation note.  When not empty it will trigger an e-mail reminder 24h before the shift's date. | *Remember to pick up the car keys from the oval office*|

<br>

>**Important!!**
>
>Some fields, like ***Role***, ***Project*** and ***Task***; will open a detailed form with the details about that specific field.
>
>For instance, if you are not sure where to go for your shift, **clicking on the project name will redirect you to the project details**, to see the location associated to this project. 
>
>(**See also section [Locations](#38-locations), to see how to get google map directions to a location.**)



<br>
<p align="center">
   <img src="gallery/planning_assigned_shift.png" alt="Assign shift conflict ask to switch" />
</p>
<center><i>Assigned shift with conflict. ***Ask to switch*** button available.</i></center>
<br>

>**Important!!**
>
> You cannot self-unassign from a shift. If you are not available for a shift that has been assigned to you, open the affected shift and press the ***Ask to switch***  button and notify your manager.

>**Important!!**
>
>You will also receive an **email notification** when your schedule is published or updated, and an automated **reminder email** 24 hours before each shift that has a preparation note.

### 3.5 Requesting an Open Shift

You can request being assigned to an open shift. **A manager will then either approve or reject that request.**

1. Go to **Planning → My Planning** (or the main Planning view)
2. Open shifts are shown without a name in the resource column
3. Click the shift to open it
4. Click **Request shift** — this sends a notification to your manager
5. Your manager will review the request and either assign you or choose a different person

<br>
<p align="center">
   <img src="gallery/planning_open_shift_form.png" alt="Open shift form view" />
</p>
<center><i>Requesting an open shift</i></center>
<br>

> You **cannot self-assign** to a shift. The *Request shift* button notifies your manager, who makes the final assignment.

### 3.6 Registering Hours
The ***Timesheets*** app of the platform allows you to register your worked hours.

The easiest way to do so, however, is via the planning app:

1. Go to **Planning → My Planning** and open the shift you want to register hours for.
2. Press the **Register hours** button. This will create a new timsheet entry and open it for you.

   <br>
   <p align="center">
      <img src="gallery/planning_assigned_shift.png" alt="Assigned shift with Register hours button" />
   </p>
   <center><i>Assigned shift. ***Register hours*** button available.</i></center>
   <br>
3. As you will see, the entry has already been pre-filled. **You don't need to change anything here** unless something changed from the initial planning (for instance if the shift took longer or shorter than initially defined). If you want, however, **you can add a description or comment** using the unnamed field immediately below ***Shift***, which by default is just populated with ***"/"*** character. 

   <br>
   <p align="center">
      <img src="gallery/timesheets_register_hours.png" alt="Timesheet entry form" />
   </p>
   <center><i>Timesheet entry with example description field</i></center>
   <br>

   > **Caution!!**
   >
   >Every time the **Register hours** button is pressed, the allocated hours will be registered. This is by design.

<br>

Alternatively, you can register your hours directly from the ***Timesheet*** app:
1. From the home menu, open the ***Timesheets*** app. This will immediately open your time sheets ***Grid*** view.
2. The grid view might already **show some of your shifts, even if you have not registered hours yet**. **This is normal**. The advantage of this view is that it shows you a whole day/week/month, so you could easily register hours for shifts that span multiple days. 

   > **Caution!!**
   >
   > **Any changes made in this view are are automatically saved**.

3. **Alternatively**, you can go to the **list view, and press ***New***** on the top left. This will immediately create a new entry (row) and ask you to **manually fill in the different fields**. Once you've filled the entry, press the ***Save*** button on the top left.

   > **Caution!!**
   >
   > **You are responsible for correctly filling the different fields. Make sure the project and tasks selected match the selected shift**.

#### What if you made a mistake?
If you realise that you've made a mistake when registering hours for a shift, you can look for the relevant entry(ies) in the ***List view*** and update or delete it/them. 
   > **Caution!!**
   >
   > **Validated entries cannot be edited or deleted**.

### 3.7 Viewing Your Timesheets
If you want to view your timesheets (to check whether they have already been validated or not, for instance), you just need to **open the Timesheets app in ***List*** or ***Calendar*** view**. You can also open a specific entry to see its state on the top right corner of the form.

<br>
   <p align="center">
      <img src="gallery/timesheets_calendar_view.png" alt="Timesheets calendar view" />
   </p>
   <center><i>My timesheets calendar view. Draft (not yet validated) entries have stripes while validated ones show solid coloring</i></center>
<br>
<br>
<br>
   <p align="center">
      <img src="gallery/timesheets_register_hours.png" alt="Timesheet entry"/>
   </p>
   <center><i>Timesheet entry. Notice validation state on the top right corner (Draft)</i></center>
<br>

### 3.8 Viewing Locations
The ***Locations*** app is a custom app that contains locations, mostly project-related locations.

A location is the combination of a **Label** and an **Address**. Additionally, notes and tags can be assigned to locations. **This can be useful, for instance, to categorize locations, or to search locations by tag later on.**

> **Important!!**
>
>Each location has an automatically generated field called ***Show in maps***. Clicking on it will open the location on google maps.

### 3.9 Viewing Protocols, protocol visits and species
The ***Protocols*** app contains information about the different species protocols and the associated species and protocol visits.

#### Protocols
You can access the details of a protocol in multiple ways. The most common are:
- ***Homepage*** → ***Protocols*** app → **Click on the protocol's name.**
- ***Planning*** → Open a ***shift*** form → associated ***Task*** → visit name → associated ***Protocol Visit*** → field ***In protocol***.

<br>
   <p align="center">
      <img src="gallery/protocols_list.png" alt="Available protocols"/>
   </p>
   <center><i>List of available protocols. Clicking on one will open its details.</i></center>
<br>

Each protocol entry shows important information regarding:
- Overarching date window for the protocol
- Remaining days for this protocol viable window.
- What type of protocol this is (Regular, SMP...)
- Species covered by this protocol
- Protocol Description.

<br>
   <p align="center">
      <img src="gallery/protocols_detail.png" alt="Protocol details"/>
   </p>
   <center><i>Protocol details</i></center>
<br>

In addition, each protocol has a tab where all its ***Protocol visits*** are listed. Pressing one will open a popup with basic information regarding the visit. **To see the full details of the visit, press on the maximize button at the top right.**

<br>
   <p align="center">
      <img src="gallery/protocols_protocol_visit_popup.png" alt="Protocol visit popup"/>
   </p>
   <center><i>Protocol visit popup. Press the top right arrows button to maximize the form and see all details regarding this visit.</i></center>
<br>

#### Protocol visits
Each protocol has a number of ***Protocol visits*** associated to it, which define the specifics of why, when, how and for whom this visit is for.

In a protocol visit entry you will find:
- What is the goal of this visit. For instance *Verblijfplaatsen van huismussen en spreeuwen*
- The Date and time window for the visit.
- Whether the visit has a dependency to a previous one (field ***Related visit***) and the minimum amount of days to wait for this visit.
- Species involved in this visit.
- Which protocol the visit belongs to
- Weather-related restrictions

<br>
   <p align="center">
      <img src="gallery/protocols_protocol_visit_detail.png" alt="Protocol visit detail"/>
   </p>
   <center><i>Protocol visit form for Huismuis visit #1.</i></center>
<br>

>**Important!** 
>
>When a protocol visit is associated with a task, a protocol visit will inform the ***Planning*** app whether a shift being created is violating the **date** or **related visit** constraints defined by the visit.

#### Species
Species entries contain relevant information about the species. 

You can **access the species** list via ***Homepage*** → ***Protocols*** app → Menu Bar → ***Species***. **Pressing an entry will open the species details.**

The information available is:
- **Name**
- **Scientific name** (optional)
- **Description** (optional)
- **Tags** (optional)
- **Protocols**: Tab that contains the list of protocols associated to this species.

<br>
   <p align="center">
      <img src="gallery/protocols_species_detail.png" alt="Species details"/>
   </p>
   <center><i>Species details of Huismuis</i></center>
<br>

### 3.10 Viewing project and tasks
All users can view the ***Project*** app. This app is where the different projects and their respective tasks can be found. The most direct way to access it is from the Homepage. In addition, you can also reach the project app by clicking a project's name, when it appears as a field in another from (for instance in a shift).

#### Projects
The main view for the ***Project*** app is the **kanban view**. Each column of this view represents a stage on the life of a project. Managers will move projects across the board -from left to right- as certain milestones are reached.
**In kanban view, clicking on a project will not open the project's details**. Instead, it will open the **project's tasks** **kanban view**. Each column, again, represening a stage a task can be in.

To see a project's settings/details:
- Open the ***Project*** app → Place the cursor over a project card → Press the 3 vertical dots button that appears → Press ***View***/***Settings***. 
or
- Open the ***Project*** app → Select ***List view*** → Click on the project's name.

<br>
   <p align="center">
      <img src="gallery/project_gantt_project_dropdown_menu.png" alt="Project card menu"/>
   </p>
   <center><i>Project card contextual menu. Pressing "View" will open the project details.</i></center>
<br>

<br>
   <p align="center">
      <img src="gallery/project_form.png" alt="Project details"/>
   </p>
   <center><i>Project details form</i></center>
<br>

The project details (project's **form view**) contains important information regarding the project: Project Leader, Parent project (if applicable), Project type, Species monitored in this project, Species protocols involved, Project manager, Location of the project...

In addition, the following tabs are present:
- ***Description***: Extra information regarding the project, in text format.
- ***Settings***: (Managers only)
- ***Shifts***: List of shifts associated to the project. 
- ***Tasks***: A list of the project's tasks.
- ***Children projects***: Only relevant for nested projects (projects of type "Master")

> Only managers/administrators can edit project details.

#### Tasks
Tasks are discrete units of work (for example a specific Protol visit) within a project. You can see if any tasks are assigned to you via:

> **Homepage** → ***Project*** App → Menu bar ***Tasks*** → ***My Tasks***.

Each task has its own Title, associated project and, optionally, Asignees, an associated **Protocol** & **Protocol Visit**, Tags, associated Customer, Deadline, Allocated time and the **number of people needed**.

Furthermore, the following tabs are available for each task:
- ***Description***: Extra information regarding this task.
- ***Timesheets***: List of timesheet entries associated with this task.
- ***Sub-tasks***: List of sub-tasks associated with this task.
- ***Blocked-by***: List of blocking tasks this task depends on.
- ***Extra Info***: Additional information.
   - ***Parent Task***: If this task is a sub-task, the parent task will be referenced here.
- ***Shifts***: List of shifts associated with this task.

   > **Important!!**
   >
   > As shifts are uni-personal instances in this new platform, *Task* is the entity that conceptually replaces the "Collective shift" idea (Protocol visit instance with multiple people associated)- from the previous system.

---

## 4. Inventory & Tools

The inventory module is accessible via **Planning → Materials**.

### Structure

Materials are organised in three levels:

```
Category  (e.g. Bat research)
  └─ Material type  (e.g. Bat detector SM4)
       └─ Material unit  (individual physical item, e.g. SM4 #003)
```

Each **material unit** has:
- A **status** (e.g. In service, Out for repair, Lost)
- A serial number (optional)
- A rental flag (if the item is rented rather than owned)
- A material type

### Linking materials to a shift

On a shift form, use the **Materials needed** field to attach one or more material *types* to the shift. This records which types of equipment are required — it does not automatically reserve individual units or deduct stock.

> Stock quantities (`booked_quantity`, `needed_stock`) are manually maintained. There is no automatic deduction when a shift is created.

### Checking what is assigned

Open any material type to see the list of individual units and their current statuses. Use the list view under **Planning → Materials → Material Types** to get an overview of available vs. booked quantities across all types.


---

## 5. Notifications & Approvals

### Notifications you will receive

| Event | Who receives it | How |
|-------|----------------|-----|
| Shift published / sent | Assigned employee | Email |
| Shift reminder | Assigned employee | Email, 24h before shift (only if a *Reminder* note is set on the shift) |
| Availability validated | Employee whose entry was validated | Inbox notification + live toast |
| Availability reset to draft | Employee | Inbox notification + live toast |
| Shift request submitted | Planning managers | To-do activity |
| Availability submitted for validation | Planning managers | To-do activity |

### Pending approvals

Planning managers can see pending availability validations as **to-do activities** in their Activity view or in the Inbox. Each activity groups all pending entries from one employee and shows the date range covered.

To validate: open the activity, review the availability entries, and click **Validate**.

---

## Appendix

### Glossary

| Term | Meaning |
|------|---------|
| **Shift** | A single work assignment: one employee, one date, one role, one project |
| **Open shift** | A shift without an assigned employee — available for employees to request |
| **Shift type** | The time-of-day category of a shift (Morning, Evening, etc.) |
| **Role** | The function performed on a shift (Field Worker, Project Leader, etc.) |
| **Availability entry** | A declaration by an employee that they are (or are not) available on a specific date for a specific shift type |
| **Validated availability** | An availability entry confirmed by a manager — required before an employee can be assigned |
| **Project** | A coordinated body of work (e.g. a monitoring contract) that contains tasks and shifts. Projects can be nested under a parent (master) project. |
| **Task** | A discrete unit of work within a project, typically corresponding to a specific protocol visit instance. Tasks group the shifts assigned to that monitoring event. |
| **Location** | A named address entry linked to a project. Includes a label, address, optional notes and tags, and a direct Google Maps link. |
| **Protocol** | A standardised monitoring procedure defining how, when, and for which species a field survey is conducted. Each protocol has a date window, a type, and one or more protocol visits. *[TODO: Tamara — add GL-Ecologie specific definition if needed]* |
| **Protocol visit** | A specific visit defined within a protocol, including a date/time window, goal, weather restrictions, species involved, and an optional dependency on a related (previous) visit. |
| **Species** | A plant or animal species tracked in the context of one or more protocols. Each entry contains a name, optional scientific name, description, tags, and a list of associated protocols. |

### Contact for support

For technical issues with the system, contact:
**Julian Ruiz Burgos** — Ruiz Burgos Ecology and Software at
`contact@julianruizburgos.net`
