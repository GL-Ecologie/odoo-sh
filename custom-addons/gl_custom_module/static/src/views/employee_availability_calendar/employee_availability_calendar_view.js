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
    
    setupCalendar() {
        const calendar = super.setupCalendar();

        const originalEventDidMount = calendar.options.eventDidMount;

        calendar.setOption("eventDidMount", (info) => {

            if (originalEventDidMount) {
                originalEventDidMount(info);
            }

            const styleKey = info.event.extendedProps?.style_key;
            console.log("Availability event styleKey:", styleKey, info.event.extendedProps);

            info.el.classList.add("o_availability_event");
            
            if (styleKey) {
                info.el.classList.add(`o_availability_${styleKey}`);
            }
        });

        return calendar;
    }
}

export const employeeAvailabilityCalendarView = {
    ...calendarView,
    Controller: EmployeeAvailabilityCalendarController,
    Renderer: EmployeeAvailabilityCalendarRenderer,
};

registry.category("views").add("employee_availability_calendar", employeeAvailabilityCalendarView);