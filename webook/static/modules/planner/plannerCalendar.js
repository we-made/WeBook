import { ArrangementInspector } from "./arrangementInspector.js";
import {
    ArrangementStore, FullCalendarBased, LocationStore,
    PersonStore, StandardColorProvider, _FC_EVENT,
    _NATIVE_ARRANGEMENT
} from "./commonLib.js";
import { EventInspector } from "./eventInspector.js";
import { FilterDialog } from "./filterDialog.js";



const monthNames = ["Januar", "Februar", "Mars", "April", "Mai", "Juni",
  "Juli", "August", "September", "Oktober", "November", "Desember"
];


export class PlannerCalendar extends FullCalendarBased {

    constructor({ 
        calendarElement, 
        eventsSrcUrl, 
        colorProviders=[], 
        initialColorProvider="",
        $locationFilterSelectEl=undefined,
        $arrangementTypeFilterSelectEl=undefined,
        $audienceTypeFilterSelectEl=undefined,
        csrf_token=undefined, calendarFilter=undefined,
        licenseKey=undefined } = {}) {

        super();

        this.csrf_token = csrf_token;
        
        this._fcLicenseKey = licenseKey;
        this._fcCalendar = undefined;
        this._calendarElement = calendarElement;
        this._eventsSrcUrl = eventsSrcUrl;

        this._colorProviders = new Map();
        this._colorProviders.set("DEFAULT", new StandardColorProvider());

        colorProviders.forEach( (bundle) => {
            this._colorProviders.set(bundle.key, bundle.provider)
        });

        // If user has not supplied an active color provider key we use default color provider as active.
        this.activeColorProvider = initialColorProvider !== undefined && this._colorProviders.has(initialColorProvider) ? this._colorProviders.get(initialColorProvider) : this._colorProviders.get("DEFAULT");
        this._ARRANGEMENT_STORE = new ArrangementStore(this.activeColorProvider);
        this._LOCATIONS_STORE = new LocationStore(this);
        this._PEOPLE_STORE = new PersonStore(this);
        this.calendarFilter = calendarFilter;

        this.init();

        this.arrangementInspectorUtility = new ArrangementInspector();
        this.eventInspectorUtility = new EventInspector();

        this.filterDialog = new FilterDialog();

        this.$locationFilterSelectEl = $locationFilterSelectEl;
        $locationFilterSelectEl.on('change', () => {
            this.init();
        });
        this.$arrangementTypeFilterSelectEl = $arrangementTypeFilterSelectEl;
        $arrangementTypeFilterSelectEl.on('change', () => {
            this.init();
        });
        this.$audienceTypeFilterSelectEl = $audienceTypeFilterSelectEl;
        $audienceTypeFilterSelectEl.on('change', () => {
            this.init();
        });
        
        this._listenToInspectArrangementEvents();
        this._listenToInspectEvent();
    }

    getFcCalendar() {
        return this._fcCalendar;
    }

    _listenToInspectArrangementEvents() {
        document.addEventListener("plannerCalendar.inspectThisArrangement", (e) => {
            var arrangement = this._ARRANGEMENT_STORE.get({
                pk: e.detail.event_pk,
                get_as: _NATIVE_ARRANGEMENT
            });
    
            this.arrangementInspectorUtility.inspect(arrangement);
        })
    }

    _listenToInspectEvent() {
        document.addEventListener("plannerCalendar.inspectEvent", (e) => {
            console.log(">> ListenToInspectEvent")
            this.eventInspectorUtility.inspect(e.detail.event_pk);
        })
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

    /**
     * Bind popover with arrangement info to elementToBindWith
     * @param {*} elementToBindWith 
     */
    _bindPopover (elementToBindWith) {
        var pk = this._findEventPkFromEl(elementToBindWith);        
        var arrangement = this._ARRANGEMENT_STORE.get({
            pk: pk,
            get_as: _NATIVE_ARRANGEMENT
        });

        if (arrangement === undefined) {
            console.error(`Could not bind popover for arrangement with pk ${pk}`);
            return;
        }

        var start = new Date(arrangement.starts)
        var end = new Date(arrangement.ends)
        start = `${
            (start.getMonth()+1).toString().padStart(2, '0')}/${
            start.getDate().toString().padStart(2, '0')}/${
            start.getFullYear().toString().padStart(4, '0')} ${
            start.getHours().toString().padStart(2, '0')}:${
            start.getMinutes().toString().padStart(2, '0')}:${
            start.getSeconds().toString().padStart(2, '0')}`
        end = `${
            (end.getMonth()+1).toString().padStart(2, '0')}/${
            end.getDate().toString().padStart(2, '0')}/${
            end.getFullYear().toString().padStart(4, '0')} ${
            end.getHours().toString().padStart(2, '0')}:${
            end.getMinutes().toString().padStart(2, '0')}:${
            end.getSeconds().toString().padStart(2, '0')}`


        var roomsListHtml = "<ul>";
        arrangement.room_names.forEach( (roomName) => {
            if (roomName !== null) {
                roomsListHtml += "<li>" + roomName + "</li>";
            }
        });
        roomsListHtml += "</ul>";
        if (roomsListHtml !== "<ul></ul>") {
            roomsListHtml = "<h6>Rom:</h6>" + roomsListHtml
        }

        var peopleListHtml = "<ul>";
        arrangement.people_names.forEach( (personName) => {
            if (personName !== null) {
                peopleListHtml += "<li>" + personName + "</li>";
            }
        })
        peopleListHtml += "</ul>";
        if (peopleListHtml !== "<ul></ul>") {
            peopleListHtml = "<h6>Personer:</h6>" + peopleListHtml;
        }

        new mdb.Popover(elementToBindWith, {
            trigger: "hover",
            content: `
                <span class='badge h6 badge-lg badge-info'>
                    Målgruppe: 
                    <i class='${arrangement.audience_icon}'></i>&nbsp;
                    ${arrangement.audience}
                </span>
                <span class='badge h6 badge-success'>
                    Hovedplanlegger:
                    ${arrangement.mainPlannerName}
                </span>
                <span class='badge h6 badge-secondary'>
                    Lokasjon: 
                    ${arrangement.location}
                </span>
                <span class='badge h6 badge-secondary'>
                    Arrangementstype: 
                    ${arrangement.arrangement_type}
                </span>
                <h5 class='mb-0 mt-2'>${arrangement.name}</h5>
                <em class='small'>${start} - ${end}</em>

                ${roomsListHtml}
                
                ${peopleListHtml}
                `,
            html: true,
        })
    }

    _bindInspectorTrigger (elementToBindWith) {
        let _this = this;
        $(elementToBindWith).on('click', (ev) => {
            var pk = _this._findEventPkFromEl(ev.currentTarget);
            // var arrangement = _this._ARRANGEMENT_STORE.get({
            //     pk: pk,
            //     get_as: _NATIVE_ARRANGEMENT
            // });
    
            this.eventInspectorUtility.inspect(pk);
        })
    }

    /**
     * First-time initialize the calendar
     */
    async init () {
        let _this = this;

        var initialView = 'timelineMonth';

        if (this._fcCalendar === undefined) {
            this._fcCalendar = new FullCalendar.Calendar(this._calendarElement, {
                schedulerLicenseKey: this._fcLicenseKey,
                initialView: initialView,
                selectable: true,
                weekNumbers: true,
                navLinks: true,
                minTime: "06:00",
                // themeSystem: 'bootstrap',
                maxTime: "23:00",
                slotEventOverlap: false,
                locale: 'nb',
                views: {
                    customTimeGridMonth: {
                        type: "timeGrid",
                        duration: { month: 1 },
                        buttonText: "Tidsgrid Måned"
                    },
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
                datesSet: (dateInfo) => {
                    $('#plannerCalendarHeader').text("");
                    $(".popover").popover('hide');

                    if (dateInfo.view.type == "timelineMonth" || dateInfo.view.type == "customTimelineMonth" || dateInfo.view.type == "dayGridMonth" || dateInfo.view.type == "customTimeGridMonth") {
                        console.log(dateInfo);
                        var monthIndex = dateInfo.start.getMonth();
                        if (dateInfo.start.getDate() !== 1) {
                            monthIndex++;
                        }
                        $('#plannerCalendarHeader').text(`${monthNames[monthIndex]} ${dateInfo.start.getFullYear()}`)
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
                headerToolbar: { left: 'arrangementsCalendarButton,locationsCalendarButton,peopleCalendarButton' , center: 'customTimeGridMonth,timeGridDay,dayGridMonth,timeGridWeek,customTimelineMonth,customTimelineYear', },
                eventSources: [
                    {
                        events: async (start, end, startStr, endStr, timezone) => {
                            return await _this._ARRANGEMENT_STORE._refreshStore(start, end)
                                .then(_ => this.calendarFilter.getFilteredSlugs().map( function (slug) { return { id: slug, name: "" } }))
                                .then(filterSet => _this._ARRANGEMENT_STORE.get_all(
                                    { 
                                        get_as: _FC_EVENT, 
                                        locations: this.$locationFilterSelectEl.val(),
                                        arrangement_types: this.$arrangementTypeFilterSelectEl.val(),
                                        audience_types: this.$audienceTypeFilterSelectEl.val(),
                                        filterSet: filterSet
                                    }
                                ));
                        },
                    }
                ],

                eventDidMount: (arg) => {
                    this._bindPopover(arg.el);
                    this._bindInspectorTrigger(arg.el);

                    $.contextMenu({
                        className: "",
                        selector: ".fc-event",
                        items: {
                            arrangement_inspector: {
                                name: "Inspiser arrangement",
                                callback: (key, opt) => {
                                    var pk = _this._findEventPkFromEl(opt.$trigger[0]);
                                    var arrangement = _this._ARRANGEMENT_STORE.get({
                                        pk: pk,
                                        get_as: _NATIVE_ARRANGEMENT
                                    });
                            
                                    this.arrangementInspectorUtility.inspect(arrangement);
                                }
                            },
                            event_inspector: {
                                name: "Inspiser tidspunkt",
                                callback: (key, opt) => {
                                    var pk = _this._findEventPkFromEl(opt.$trigger[0]);
                                    this.eventInspectorUtility.inspect(pk);
                                }
                            },
                            "section_sep_1": "---------",
                            delete_arrangement: {
                                name: "Slett arrangement",
                                callback: (key, opt) => {
                                    Swal.fire({
                                        title: 'Er du sikker?',
                                        text: "Arrangementet og underliggende aktiviteter vil bli fjernet, og kan ikke hentes tilbake.",
                                        icon: 'warning',
                                        showCancelButton: true,
                                        confirmButtonColor: '#3085d6',
                                        cancelButtonColor: '#d33',
                                        confirmButtonText: 'Ja',
                                        cancelButtonText: 'Avbryt'
                                    }).then((result) => {
                                        if (result.isConfirmed) {
                                            var slug = _this._findSlugFromEl(opt.$trigger[0]);
                                            fetch('/arrangement/arrangement/delete/' + slug, {
                                                method: 'DELETE',
                                                headers: {
                                                    "X-CSRFToken": this.csrf_token
                                                }
                                            }).then(_ => { 
                                                document.dispatchEvent(new Event("plannerCalendar.refreshNeeded")); // Tell the planner calendar that it needs to refresh the event set
                                            });
                                        }
                                    })
                                }
                            },
                            delete_event: {
                                name: "Slett aktivitet",
                                callback: (key, opt) => {
                                    Swal.fire({
                                        title: 'Er du sikker?',
                                        text: "Hendelsen kan ikke hentes tilbake.",
                                        icon: 'warning',
                                        showCancelButton: true,
                                        confirmButtonColor: '#3085d6',
                                        cancelButtonColor: '#d33',
                                        confirmButtonText: 'Ja',
                                        cancelButtonText: 'Avbryt'
                                    }).then((result) => {
                                        if (result.isConfirmed) {
                                            var pk = _this._findEventPkFromEl(opt.$trigger[0]);

                                            var formData = new FormData();
                                            formData.append("eventIds", String(pk));

                                            fetch('/arrangement/planner/delete_events/', {
                                                method: 'POST',
                                                body: formData,
                                                headers: {
                                                    "X-CSRFToken": this.csrf_token,
                                                }
                                            }).then(_ => { 
                                                document.dispatchEvent(new Event("plannerCalendar.refreshNeeded")); // Tell the planner calendar that it needs to refresh the event set
                                            });
                                        }
                                    })
                                }
                            }
                        }
                    });
                }
            })
        }
        else {
            // initialView = this._fcCalendar.view.type;
            this._fcCalendar.refetchEvents();
        }

        this._fcCalendar.render();
    }
}