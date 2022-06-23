import { convertObjToFormData } from "./commonLib.js";
import { serieConvert } from "./serieConvert.js";


const COMMA_SEPARATED_LIST_SPLITS = ["display_layouts", "rooms", "people"];

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
        formData.append("arrangementPk", arrangement_pk);
        if ("event_serie_pk" in serie) {
            formData.append("predecessorSerie", serie.event_serie_pk);
        }

        for (var value of formData) {
            console.log(value);
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
    static async SaveEvents(events, csrf_token, preset_formdata = undefined) {
        var formData = preset_formdata !== undefined && preset_formdata instanceof FormData ? preset_formdata : new FormData();
        for (var i = 0; i < events.length; i++) {
            var event = events[i];
            for (var key in event) {
                formData.append("events[" + i + "]." + key, event[key]);
            }
        }

        var evMap = new Map();
        for (var event_pair of formData.entries()) {
            var key_without_index = event_pair[0].split(".")[1];
            var index = event_pair[0].slice(6, 1)

            var event = {};

            if (evMap.has(index)) {
                event = evMap.get(index);
            }

            if (COMMA_SEPARATED_LIST_SPLITS.includes(key_without_index)) {
                event_pair[1] = event_pair[1].split(",");
            }

            event[key_without_index] = event_pair[1];
            evMap.set(index, event);
        }

        for (const ev of evMap) {
            var formData = convertObjToFormData(ev[1], true);

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
}