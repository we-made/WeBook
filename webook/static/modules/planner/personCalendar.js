import { FullCalendarEvent, FullCalendarResource, FullCalendarBased, LocationStore, _FC_RESOURCE, PersonStore } from "./commonLib.js";


export class PersonCalendar extends FullCalendarBased {

    constructor ( {calendarElement } = {} ) {
        super();

        this._fcCalendar = undefined;
        this._calendarElement = calendarElement;
        
        this._STORE = new PersonStore(this);

        this.init()
    }

    refresh() {
        console.info("HIT REFRESH")
        this.init()
    }

    _bindPopover() {

    }

    init() {
        let _this = this;

        if (this._fcCalendar === undefined) {
            this._fcCalendar = new FullCalendar.Calendar(_this._calendarElement, {
                headerToolbar: { center: 'resourceTimelineMonth,resourceTimelineWeek' },
                initialView: 'resourceTimelineMonth',
                selectable: true,
                themeSystem: 'bootstrap',
                views: {
                    resourceTimelineMonth: {
                      type: 'resourceTimeline',
                      duration: { month: 1 }
                    }
                },
                eventRender: function (event, element, view) {
                    $(element).find(".fc-list-item-title").append("<div>" + event.resourceId + "</div>");
                },
                navLinks: true,
                locale: 'nb',
                events: [ { title: "Test Arrangement", start: "2022-03-01", end: "2022-03-30", resourceId: 'lokasjon-3'  } ],
                resources: async (fetchInfo, successCallback, failureCallback) => {
                    await _this._STORE._refreshStore();
                    successCallback(_this._STORE.getAll({ get_as: _FC_RESOURCE }));
                },
            });
        }

        this._fcCalendar.render();
    }
}