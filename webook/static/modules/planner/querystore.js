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

        const response = await fetch('/arrangement/event/create_serie', {
            method: 'POST',
            body: formData,
            headers: {
                "X-CSRFToken": csrf_token
            },
            credentials: 'same-origin',
        }).then(response => response.json());

        const responseData = response;
        console.log("RESPONSE", responseData)

        debugger;

        if ("ordered_services" in serie)
        {
            // x.service_order === null to make sure we only do orderservice create on new orders.
            // existing orders on predecessor serie will be handled on the creation of the serie
            serie.ordered_services.filter(x => x.service_order === null).forEach(async (serviceOrder) => {
                let formData = new FormData();
                formData.append("parent_type", "serie");
                formData.append("parent_id", responseData.id);
                formData.append("service_id", serviceOrder.service_id);
                formData.append("freetext_comment", serviceOrder.freetext_comment);
                if (serviceOrder.service_order)
                    formData.append("service_order", serviceOrder.service_order);

                await fetch('/arrangement/planner/dialogs/order_service/serie/' + responseData.id, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        "X-CSRFToken": csrf_token
                    }
                });
            });
        }
            

        return response;
    }

    /**
     * Save an array of events
     * @param {*} events 
     * @param {*} csrf_token 
     * @param {*} preset_formdata Pass a custom FormData instance in to inject values, or let be undefined for standard
     * @returns {*} promise
     */
    static async SaveEvents(events, csrf_token) {
        for (const [event, formData] of events.map((event) => [ event, convertObjToFormData(event, true) ])) {
            const response = await fetch("/arrangement/event/create", {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": csrf_token
                },
                credentials: 'same-origin',
            }).then(response => response.json());

            if (response.success === false)
                throw Error("Failed creating event", response);

            if ("ordered_services" in event)
            {
                event.ordered_services.forEach(async (serviceOrder) => {
                    let formData = new FormData();
                    formData.append("parent_type", "event");
                    formData.append("parent_id", response.id);
                    formData.append("service_id", serviceOrder.service_id);
                    formData.append("freetext_comment", serviceOrder.freetext_comment);

                    await fetch('/arrangement/planner/dialogs/order_service/event/' + response.id, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            "X-CSRFToken": csrf_token
                        }
                    }).then(response => response.json());
                });
            }
        }
    }


    static async UpdateEvents (events, csrf_token) {
        let responses = [];
        for (const formData of events.map((event) => convertObjToFormData(event, true))) {
            let response = await fetch("/arrangement/planner/update_event/" + formData.get("id"), {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": csrf_token
                },
                credentials: 'same-origin',
            })
            responses.push(await response.json())
        }
        return responses;
    }


    /**
     * Get the serie manifest for a given serie identified by serie_pk
     * @param {*} serie_pk 
     * @returns 
     */
    static async GetSerieManifest(serie_pk) {
        return await fetch(`/arrangement/eventSerie/${serie_pk}/manifest`, {
            method: "GET"
        }).then(async response => { let resp = await response.json(); console.log("resp", resp); return resp; });
    }
}