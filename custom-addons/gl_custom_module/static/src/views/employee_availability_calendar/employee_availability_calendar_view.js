import { registry } from "@web/core/registry";
import { calendarView } from "@web/views/calendar/calendar_view";
import { CalendarController } from "@web/views/calendar/calendar_controller";
import { CalendarRenderer } from "@web/views/calendar/calendar_renderer";
import { CalendarCommonRenderer} from "@web/views/calendar/calendar_common/calendar_common_renderer";
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

class EmployeeAvailabilityCalendarCommonRenderer extends CalendarCommonRenderer {
    eventClassNames(params) {
        const classes = super.eventClassNames(params);

        const record = this.props.model.records[params.event.id];
        if (!record) {
            return classes;
        }
        classes.push("o_availability_event");

        const styleKey = record.rawRecord?.style_key;
        
        if (styleKey) {
            classes.push(`o_availability_${styleKey}`);
        }

        return classes;
    }
}

class EmployeeAvailabilityCalendarRenderer extends CalendarRenderer {
    static components = {
        ...CalendarRenderer.components,
        day: EmployeeAvailabilityCalendarCommonRenderer,
        week: EmployeeAvailabilityCalendarCommonRenderer,
        month: EmployeeAvailabilityCalendarCommonRenderer,
    };
}

export const employeeAvailabilityCalendarView = {
    ...calendarView,
    Controller: EmployeeAvailabilityCalendarController,
    Renderer: EmployeeAvailabilityCalendarRenderer,
};

registry.category("views").add("employee_availability_calendar", employeeAvailabilityCalendarView);