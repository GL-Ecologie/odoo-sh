import { registry } from "@web/core/registry";
import { calendarView } from "@web/views/calendar/calendar_view";
import { CalendarController } from "@web/views/calendar/calendar_controller";
import { Component } from "@odoo/owl";

class AvailabilityLegend extends Component {
    static template = "gl_custom_module.AvailabilityCalendarLegend";
}

class EmployeeAvailabilityCalendarController extends CalendarController {
    static components = {
        ...CalendarController.components,
        AvailabilityLegend,
    };
}

export const employeeAvailabilityCalendarView = {
    ...calendarView,
    Controller: EmployeeAvailabilityCalendarController,
};

registry.category("views").add("employee_availability_calendar", employeeAvailabilityCalendarView);