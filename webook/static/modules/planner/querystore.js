import { serieConvert } from "./serieConvert.js";
import { SeriesUtil } from "./seriesutil.js";

/**
 * A store of common queries
 */
export class QueryStore {
    /**
     * Save a serie
     * @param {*} serie the serie which we are to save
     * @param {*} csrf_token 
     */
    static async SaveSerie(serie, csrf_token, arrangement_pk=0) {
        var formData = serieConvert(serie, new FormData());
        formData.append("saveAsSerie", true);
        var events = SeriesUtil.calculate_serie(serie);
        
        events.forEach(function (event) { 
            event.arrangement = arrangement_pk;
            event.expected_visitors = serie.time.expected_visitors;
            event.start = event.from.toISOString();
            event.end= event.to.toISOString();
            event.ticket_code = serie.time.ticket_code;
            event.expected_visitors = serie.time.expected_visitors;
            event.rooms = serie.rooms;
            event.people = serie.people;
            event.display_layouts = serie.display_layouts;
        });

        return this.SaveEvents(events, csrf_token, formData);
    }

    /**
     * Save an array of events
     * @param {*} events 
     * @param {*} csrf_token 
     * @param {*} preset_formdata Pass a custom FormData instance in to inject values, or let be undefined for standard
     * @returns {*} promise
     */
    static async SaveEvents(events, csrf_token, preset_formdata=undefined) {
        var formData = preset_formdata !== undefined && preset_formdata instanceof FormData ? preset_formdata : new FormData();
        for (var i = 0; i < events.length; i++) {
            var event = events[i];
            for (var key in event) {
                formData.append("events[" + i + "]." + key, event[key]);
            }
        }

        return await fetch("/arrangement/planner/create_events/", {
            method:"POST",
            body: formData,
            headers: {
                "X-CSRFToken": csrf_token
            },
            credentials: 'same-origin',
        });
    }
}