import { convertObjToFormData, getClientTimezone } from "./commonLib.js";
import { serieConvert } from "./serieConvert.js";


const COMMA_SEPARATED_LIST_SPLITS = ["rooms", "people", "display_layouts"];

/**
 * A store of common queries
 */
export class QueryStore {
    /**
     * Save a serie
     * @param {*} serie the serie which we are to save
     * @param {*} csrf_token 
     */
    static async SaveSerie(serie, csrf_token, arrangement_pk = 0) {
        var formData = serieConvert(serie, new FormData(), "");
        formData.append("timezone", getClientTimezone());
        formData.append("arrangementPk", arrangement_pk);
        if ("event_serie_pk" in serie) {
            formData.append("predecessorSerie", serie.event_serie_pk);
        }

        for (var pair of formData.entries()) {
            console.log(pair[0]+ ', ' + pair[1]);
        }

        return await fetch('/arrangement/event/create_serie', {
            method: 'POST',
            body: formData,
            headers: {
                "X-CSRFToken": csrf_token
            },
            credentials: 'same-origin',
        });
    }

    /**
     * Save an array of events
     * @param {*} events 
     * @param {*} csrf_token 
     * @param {*} preset_formdata Pass a custom FormData instance in to inject values, or let be undefined for standard
     * @returns {*} promise
     */
    static async SaveEvents(events, csrf_token) {
        console.log("events", events)
        for (const formData of events.map((event) => convertObjToFormData(event, true))) {
            await fetch("/arrangement/event/create", {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": csrf_token
                },
                credentials: 'same-origin',
            })
        }
    }


    static async UpdateEvents (events, csrf_token) {
        for (const formData of events.map((event) => convertObjToFormData(event, true))) {
            await fetch("/arrangement/planner/update_event/" + formData.get("id"), {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": csrf_token
                },
                credentials: 'same-origin',
            })
        }
    }


    /**
     * Get the serie manifest for a given serie identified by serie_pk
     * @param {*} serie_pk 
     * @returns 
     */
    static async GetSerieManifest(serie_pk) {
        return await fetch(`/arrangement/eventSerie/${serie_pk}/manifest`, {
            method: "GET"
        }).then(response => response.json());
    }
}