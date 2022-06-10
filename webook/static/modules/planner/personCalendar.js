import { ArrangementStore, FullCalendarBased, PersonStore, StandardColorProvider, _FC_EVENT, _FC_RESOURCE } from "./commonLib.js";
import { monthNames } from "./monthNames.js";

export class PersonCalendar extends FullCalendarBased {

    constructor ( {calendarElement, initialColorProvider="", colorProviders=[], calendarFilter=undefined  } = {} ) {
        super();

        this._fcCalendar = undefined;
        this._calendarElement = calendarElement;
        
        this._colorProviders = new Map();
        this._colorProviders.set("DEFAULT", new StandardColorProvider());

        colorProviders.forEach( (bundle) => {
            this._colorProviders.set(bundle.key, bundle.provider)
        });

        // If user has not supplied an active color provider key we use default color provider as active.
        // this.activeColorProvider = initialColorProvider !== undefined && this._colorProviders.has(initialColorProvider) ? initialColorProvider : this._colorProviders.get("DEFAULT");

        this.calendarFilter = calendarFilter;
        this._ARRANGEMENT_STORE = new ArrangementStore(this._colorProviders.get("arrangement"));
        this._STORE = new PersonStore(this);

        this.init()
    }

    getFcCalendar() {
        return this._fcCalendar;
    }

    refresh() {
        this.init()
    }

    _bindPopover() {

    }

    async init() {
        let _this = this;

        if (this._fcCalendar === undefined) {
            this._fcCalendar = new FullCalendar.Calendar(_this._calendarElement, {
                headerToolbar: { left: 'arrangementsCalendarButton,locationsCalendarButton,peopleCalendarButton' , center: 'resourceTimelineMonth,resourceTimelineWeek' },
                initialView: 'resourceTimelineMonth',
                selectable: true,
                customButtons: {
                    filterButton: {
                        text: 'Filtrering',
                        click: () => {
                            this.filterDialog.openFilterDialog();
                        }
                    },
                    arrangementsCalendarButton: {
                        text: 'Arrangementer',
                        click: () => {
                            $('#overview-tab')[0].click();
                        }
                    },
                    locationsCalendarButton: {
                        text: 'Lokasjoner',
                        click: () => {
                            $('#locations-tab')[0].click();
                        }
                    },
                    peopleCalendarButton: {
                        text: 'Personer',
                        click: () => {
                            $('#people-tab')[0].click();
                        }
                    }
                },
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
                eventSources: [
                    {
                        events: async (start, end, startStr, endStr, timezone) => {
                            return await _this._ARRANGEMENT_STORE._refreshStore(start, end)
                                .then(_ => this.calendarFilter.getFilteredSlugs().map( function (slug) { return { id: slug, name: "" } }))
                                .then(filterSet => _this._ARRANGEMENT_STORE.get_all(
                                    { 
                                        get_as: _FC_EVENT, 
                                        locations: undefined,
                                        arrangement_types: undefined,
                                        audience_types: undefined,
                                        filterSet: undefined
                                    }
                                ));
                        },
                    }
                ],
                datesSet: (dateInfo) => {
                    $('#plannerCalendarHeader').text("");
                    $(".popover").popover('hide');
    
                    if (dateInfo.view.type == "resourceTimelineMonth") {
                        var monthIndex = dateInfo.start.getMonth();
                        if (dateInfo.start.getDate() !== 1) {
                            monthIndex++;
                        }
                        $('#plannerCalendarHeader').text(`${monthNames[monthIndex]} ${dateInfo.start.getFullYear()}`)
                    }
                },
                resources: async (fetchInfo, successCallback, failureCallback) => {
                    await _this._STORE._refreshStore();
                    successCallback(_this._STORE.getAll({ get_as: _FC_RESOURCE }));
                },
            });
        }
        else {
            this._fcCalendar.refetchEvents();
        }

        this._fcCalendar.render();
    }
}