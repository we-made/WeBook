import { FullCalendarEvent, FullCalendarResource } from "./commonLib.js";


export class PlannerLocationCalendar {

    constructor ( {calendarElement } = {} ) {
        super();

        this._fcCalendar = undefined;
        this._calendarElement = calendarElement;
        
        this._initCalendar()
    }

    _bindPopover() {

    }

    init() {
        let _this = this;
        this._fcCalendar = new FullCalendar.Calendar(this._calendarElement, {
            initialView: 'timeGridWeek',
        });

        this._fcCalendar.render();
    }
}