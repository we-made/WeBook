import { 
    FullCalendarEvent, 
    FullCalendarResource, 
    FullCalendarBased, 
    writeSlugClass, 
    ArrangementStore, 
    _FC_EVENT, 
    _NATIVE_ARRANGEMENT, 
    LocationStore,
    PersonStore,
    _FC_RESOURCE,
} from "./commonLib.js";

import { ArrangementInspector } from "./arrangementInspector.js";
import { FilterDialog } from "./filterDialog.js";

export class PlannerCalendar extends FullCalendarBased {

    constructor( { calendarElement, eventsSrcUrl, colorProviders=[], initialColorProvider="" } = {}) {
        super();

        this._fcCalendar = undefined;
        this._calendarElement = calendarElement;
        this._eventsSrcUrl = eventsSrcUrl;

        this._colorProviders = new Map();
        this._colorProviders.set("DEFAULT", new this.StandardColorProvider());

        colorProviders.forEach( (bundle) => {
            this._colorProviders.set(bundle.key, bundle.provider)
        });

        // If user has not supplied an active color provider key we use default color provider as active.
        this.activeColorProvider = initialColorProvider !== undefined && this._colorProviders.has(initialColorProvider) ? initialColorProvider : "DEFAULT";

        this._ARRANGEMENT_STORE = new ArrangementStore(this);
        this._LOCATIONS_STORE = new LocationStore(this);
        this._PEOPLE_STORE = new PersonStore(this);

        this.init();

        this.inspectorUtility = new ArrangementInspector();
        this.filterDialog = new FilterDialog();
    }

    /**
     * The standard calendar color provider
     */
    StandardColorProvider = class StandardColorProvider {
        getColor(arrangement) {
            return "green";
        }
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

    /**
     * Get the currently active color provider instance
     * @returns active color provider
     */
    _getColorProvider() {
        return this._colorProviders.get(this.activeColorProvider);
    }

    /**
     * Bind popover with arrangement info to elementToBindWith
     * @param {*} elementToBindWith 
     */
    _bindPopover (elementToBindWith) {
        var slug = this._findSlugFromEl(elementToBindWith);        
        var arrangement = this._ARRANGEMENT_STORE.get({
            slug: slug,
            get_as: _NATIVE_ARRANGEMENT
        });

        if (arrangement === undefined) {
            console.error(`Could not bind popover for arrangement with slug ${slug}`);
            return;
        }

        new mdb.Popover(elementToBindWith, {
            trigger: "hover",
            content: `
                <span class='badge badge-lg badge-info'>
                    <i class='${arrangement.audience_icon}'></i>&nbsp;
                    ${arrangement.audience}
                </span>
                <span class='badge h6 badge-success'>
                    ${arrangement.mainPlannerName}
                </span>
                <h5 class='mb-0 mt-2'>${arrangement.name}</h5>
                <em class='small'>${arrangement.starts} - ${arrangement.ends}</em>
                `,
            html: true,
        })
    }

    _bindInspectorTrigger (elementToBindWith) {
        let _this = this;
        $(elementToBindWith).on('click', (ev) => {
            var slug = _this._findSlugFromEl(ev.currentTarget);
            console.log(">> Slug: " + slug)
            var arrangement = _this._ARRANGEMENT_STORE.get({
                slug: slug,
                get_as: _NATIVE_ARRANGEMENT
            });
    
            this.inspectorUtility.inspectArrangement(arrangement);
        })
    }

    /**
     * First-time initialize the calendar
     */
    async init () {
        let _this = this;
        this._fcCalendar = new FullCalendar.Calendar(this._calendarElement, {
            initialView: 'dayGridMonth',
            selectable: true,
            // themeSystem: 'bootstrap',
            weekNumbers: true,
            navLinks: true,
            locale: 'nb',
            views: {
                calendarDayGridMonth: {
                    type: 'dayGridMonth',
                    buttonText: 'Kalender'
                },
                customTimelineMonth: {
                    type: 'timelineMonth',
                    buttonText: 'Tidslinje - Måned'
                },
                customTimelineYear: {
                    type: 'timelineYear',
                    buttonText: 'Tidslinje - År'
                }
            },
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
                        $('#overview-tab').trigger('click');
                    }
                },
                locationsCalendarButton: {
                    text: 'Lokasjoner',
                    click: () => {
                        $('#locations-tab').trigger('click');
                    }
                },
                peopleCalendarButton: {
                    text: 'Personer',
                    click: () => {
                        $('#people-tab').trigger('click');
                    }
                }
            },
            headerToolbar: { left: 'arrangementsCalendarButton,locationsCalendarButton,peopleCalendarButton' , center: 'calendarDayGridMonth,customTimelineMonth,customTimelineYear', },
            events: async (start, end, startStr, endStr, timezone) => {
                return await _this._ARRANGEMENT_STORE._refreshStore(start, end)
                        .then(a => _this._ARRANGEMENT_STORE.get_all({ get_as: _FC_EVENT }));
            },


            eventContent: (arg) => {
                var icon_class = arg.event.extendedProps.icon;
                let html = `<span class="h6"
                                    data-toggle='tooltip'
                                    title='Right click me to get options'>
  
                                <span class='text-white ms-2'>
                                    <i class='${icon_class}'></i>
                                </span>
                                <em class='small'>${arg.event.extendedProps.starts} - ${arg.event.extendedProps.ends}</em>
                                ${arg.event.title}
                            </span>`
                return { html: html }
            },
            eventDidMount: (arg) => {
                this._bindPopover(arg.el);
                this._bindInspectorTrigger(arg.el);

                $.contextMenu({
                    className: "",
                    selector: ".fc-event",
                    items: {
                        open: {
                            name: "Open",
                            icon: "",
                            isHtmlName: false,
                            callback: (key, opt) => {
                                location.href = "/arrangement/arrangement/" + this._findSlugFromEl(opt.$trigger[0]);
                            }
                        },
                        edit: {
                            name: "Edit",
                            icon: "edit",
                            isHtmlName: false,
                            callback: (key, opt) => {
                                location.href = "/arrangement/arrangement/edit/" + this._findSlugFromEl(opt.$trigger[0]);
                            }
                        },
                        audience: {
                            name: "Status",
                            type: "select",
                            options: { 1: "Planlegges", 2: "Venter kvittering", 3: "Ferdig" }
                        }
                    }
                });
            }
        });

        this._fcCalendar.render();
    }
}