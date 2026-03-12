import { registry } from "@web/core/registry";
import { calendarView } from "@web/views/calendar/calendar_view";
import { CalendarController } from "@web/views/calendar/calendar_controller";
import { CalendarRenderer } from "@web/views/calendar/calendar_renderer";
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

class EmployeeAvailabilityCalendarRenderer extends CalendarRenderer {
    get options() {
        const options = super.options;
        const superEventDidMount = options.eventDidMount;

        options.eventDidMount = (info) => {
            if (superEventDidMount) {
                superEventDidMount(info);
            }

            info.el.classList.add("o_availability_event");

            const styleKey = info.event.extendedProps?.style_key;
            if (styleKey) {
                info.el.classList.add(`o_availability_${styleKey}`);
            }
        };

        return options;
    }
}

export const employeeAvailabilityCalendarView = {
    ...calendarView,
    Controller: EmployeeAvailabilityCalendarController,
    Renderer: EmployeeAvailabilityCalendarRenderer,
};

registry.category("views").add("employee_availability_calendar", employeeAvailabilityCalendarView);