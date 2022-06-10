import { HeaderGenerator } from "./calendar_utilities/header_generator.js";
import { ArrangementStore, FullCalendarBased, LocationStore, StandardColorProvider, _FC_EVENT, _FC_RESOURCE } from "./commonLib.js";


export class LocationCalendar extends FullCalendarBased {

    constructor ( {calendarElement,  colorProviders=[], initialColorProvider="", calendarFilter=undefined  } = {} ) {
        super();

        this._fcCalendar = undefined;
        this._calendarElement = calendarElement;
        this.calendarFilter = calendarFilter;

        this._headerGenerator = new HeaderGenerator();

        this._colorProviders = new Map();
        this._colorProviders.set("DEFAULT", new StandardColorProvider());

        colorProviders.forEach( (bundle) => {
            this._colorProviders.set(bundle.key, bundle.provider)
        });

        // // If user has not supplied an active color provider key we use default color provider as active.
        // this.activeColorProvider = initialColorProvider !== undefined && this._colorProviders.has(initialColorProvider) ? initialColorProvider : this._colorProviders.get("DEFAULT");

        this._ARRANGEMENT_STORE = new ArrangementStore(this._colorProviders.get("arrangement"));
        this._LOCATIONS_STORE = new LocationStore(this);

        this.init()
    }

    getFcCalendar() {
        return this._fcCalendar;
    }

    /**
     * Set a new active color provider, identified by the given key. 
     * Set color provider must have been registered on initialization of planner calendar.
     * @param {*} key 
     */
    setActiveColorProvider(key) {
        if (this._colorProviders.has(key)) {
            this.activeColorProvider = key;
        }
        else {
            console.error(`Color provider with the given key: '${this.key}' does not exist.`)
        }
    }

    // /**
    //  * Get the currently active color provider instance
    //  * @returns active color provider
    //  */
    _getColorProvider() {
        return this._colorProviders.get(this.activeColorProvider);
    }

    refresh() {
        this.init()
    }

    async init() {
        let _this = this;

        if (this._fcCalendar === undefined) {
            this._fcCalendar = new FullCalendar.Calendar(_this._calendarElement, {
                initialView: 'resourceTimelineMonth',
                headerToolbar: { left: 'arrangementsCalendarButton,locationsCalendarButton,peopleCalendarButton', center: 'resourceTimelineMonth,resourceTimelineWeek' },
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
                    // $(element).find(".fc-list-item-title").append("<div>" + event.resourceId + "</div>");
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
    
                    $('#plannerCalendarHeader').text(this._headerGenerator.generate(
                        dateInfo.view.type,
                        dateInfo.start,
                    ));
                },
                resources: async (fetchInfo, successCallback, failureCallback) => {
                    await _this._LOCATIONS_STORE._refreshStore();
                    successCallback(_this._LOCATIONS_STORE.getAll({ get_as: _FC_RESOURCE }));
                },
                resourceLabelContent: function (arg) {
                    var domNodes = [];

                    var name = document.createElement("span");
                    name.innerText = arg.resource.title;

                    if (arg.resource.extendedProps.resourceType === "location") {
                        name.classList.add("fw-bolder");
                    }
                    else {
                        name.innerHTML = `${name.innerText} <abbr title="Maks kapasitet på dette rommet"><em class='small text-muted'>(${arg.resource.extendedProps.maxCapacity})</em></abbr>`;
                    }

                    domNodes.push(name);

                    if (arg.resource.extendedProps.resourceType === "location") {
                        var linkWrapper = document.createElement("span")
                        linkWrapper.innerHTML=`<a href='/arrangement/location/${arg.resource.id}' class='ms-3'><i class='fas fa-arrow-right'></i></a>`;
                        domNodes.push(linkWrapper);
                    }

                    return { domNodes: domNodes };
                }
            });
        }
        else {
            this._fcCalendar.refetchEvents();
        }

        this._fcCalendar.render();
    }
}