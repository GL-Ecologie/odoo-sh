import { registry } from "@web/core/registry";
import { calendarView } from "@web/views/calendar/calendar_view";
import { CalendarController } from "@web/views/calendar/calendar_controller";
import { CalendarRenderer } from "@web/views/calendar/calendar_renderer";
import { CalendarCommonRenderer} from "@web/views/calendar/calendar_common/calendar_common_renderer";
import { MultiSelectionButtons } from "@web/views/view_components/multi_selection_buttons";
import { Component, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";


class AvailabilityLegend extends Component {
    static template = "gl_custom_module.AvailabilityCalendarLegend";
    static props = ["*"];
}

class EmployeeAvailabilityMultiSelectionButtons extends MultiSelectionButtons {
    static template = "gl_custom_module.EmployeeAvailabilityMultiSelectionButtons";
    static props = {
        reactive: {
            type: Object,
            shape: {
                ...MultiSelectionButtons.props.reactive.shape,
                isManager: Boolean,
                onBatchEdit: Function,
                onBatchValidate: Function,
                onBatchResetToDraft: Function,
            },
        },
    };
}

class EmployeeAvailabilityCalendarController extends CalendarController {
    static components = {
        ...CalendarController.components,
        AvailabilityLegend,
        MultiSelectionButtons: EmployeeAvailabilityMultiSelectionButtons,
    };

    setup() {
        super.setup();
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.userService = useService("user");

        onWillStart(async () => {
            const isManager = await this.userService.hasGroup("planning.group_planning_manager");
            this.multiSelectionButtonsReactive.isManager = isManager;
        });
    }

    prepareMultiSelectionButtonsReactive() {
        const result = super.prepareMultiSelectionButtonsReactive();
        result.isManager = false;
        result.onBatchEdit = () => this.onBatchEdit();
        result.onBatchValidate = () => this.onBatchValidate();
        result.onBatchResetToDraft = () => this.onBatchResetToDraft();
        return result;
    }

    get selectedIds() {
        return this.selectedCells ? this.getSelectedRecordIds(this.selectedCells) : [];
    }

    async onBatchEdit() {
        const ids = this.selectedIds;
        if (!ids.length) return;
        const action = await this.orm.call(
            "planning.employee_availability_batch_edit_wizard",
            "action_open_wizard",
            [],
            { context: { active_ids: ids } }
        );
        await this.actionService.doAction(action, {
            onClose: () => this.model.load(),
        });
    }

    async onBatchValidate() {
        const ids = this.selectedIds;
        if (!ids.length) return;
        await this.orm.call("planning.employee_availability_entry", "action_validate", [ids]);
        await this.model.load();
    }

    async onBatchResetToDraft() {
        const ids = this.selectedIds;
        if (!ids.length) return;
        await this.orm.call("planning.employee_availability_entry", "action_reset_to_draft", [ids]);
        await this.model.load();
    }
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
