export function PopulateCreateSerieDialogFromSerie(serie, $dialogElement, dialog) {
    if (serie === undefined) {
        console.error("Serie is undefined", serie);
        debugger;
    }

    [
        { target: '#serie_uuid', value: serie._uuid },
        { target: '#serie_title', value: serie.time.title },
        { target: '#serie_title_en', value: serie.time.title_en },
        { target: '#serie_start', value: serie.time.start },
        { target: '#serie_end', value: serie.time.end },
        { target: '#serie_ticket_code', value: serie.time.ticket_code },
        { target: '#serie_expected_visitors', value: serie.time.expected_visitors },
        { target: '#area_start_date', value: serie.time_area.start_date },
        { target: '#buffer_before_start', value: serie.buffer.before?.start },
        { target: '#buffer_before_end', value: serie.buffer.before?.after },
        { target: '#buffer_after_start', value: serie.buffer.after?.start },
        { target: '#buffer_after_end', value: serie.buffer.after?.end },
        { target: '#id_status', value: serie.time.status },
        { target: '#_backingArrangementTypeId', value: serie.time.arrangement_type },
        { target: '#_backingAudienceId', value: serie.time.audience },
        { target: '#id_responsible', value: serie.time.responsible },
        { target: '#id_meeting_place', value: serie.time.meeting_place },
        { target: '#id_meeting_place_en', value: serie.time.meeting_place_en },
        { target: '#display_text', value: serie.time.display_text },
        { target: '#display_text_en', value: serie.time.display_text_en },
    ].forEach( (mapping) => {
        $dialogElement.find( mapping.target ).val( mapping.value );
    } );

    // This is fairly messy I am afraid, but the gist of what we're doing here is simulating that the user
    // has "selected" rooms as they would through the dialog interface.
    if (serie.people.length > 0) {
        let peopleSelectContext = Object();
        peopleSelectContext.people = serie.people.join(",");
        peopleSelectContext.people_name_map = serie.people_name_map;
        document.dispatchEvent(new CustomEvent(
            "arrangementCreator.d2_peopleSelected",
            { detail: {
                context: peopleSelectContext
            } }
        ));
    }
    if (serie.rooms.length > 0) {
        let roomSelectContext = Object();
        roomSelectContext.rooms = serie.rooms.join(",");
        roomSelectContext.room_name_map = serie.room_name_map;
        document.dispatchEvent(new CustomEvent(
            "arrangementCreator.d2_roomsSelected",
            { detail: {
                context: roomSelectContext
            } }
        ));
    }

    serie.display_layouts.split(",").forEach(element => {
        $dialogElement.find('#id_display_layouts_serie_planner_' + element).prop( "checked", true );
    });

    switch(serie.time_area.method_name) {
        case "StopWithin":
            $dialogElement.find('#radio_timeAreaMethod_stopWithin').prop("checked", true);
            $dialogElement.find('#area_stopWithin').val(serie.time_area.stop_within);
            $dialogElement.find('#area_stopWithin')[0].disabled = false;
            break;
        case "StopAfterXInstances":
            $dialogElement.find('#radio_timeAreaMethod_stopAfterXInstances').prop("checked", true);
            $dialogElement.find('#area_stopAfterXInstances').val(serie.time_area.instances);
            $dialogElement.find('#area_stopAfterXInstances')[0].disabled = false;
            break;
        case "NoStopDate":
            $dialogElement.find('#radio_timeAreaMethod_noStopDate').prop("checked", true);
            $dialogElement.find('#area_noStop_projectXMonths').val(serie.time_area.projectionDistanceInMonths);
            $dialogElement.find('#area_noStop_projectXMonths')[0].disabled = false;
            break;
    }

    switch(serie.pattern.pattern_type) {
        case "daily":
            $dialogElement.find('#radio_pattern_daily').prop("checked", true);
            switch(serie.pattern.pattern_routine) {
                case "daily__every_x_day":
                    $dialogElement.find('#radio_pattern_daily_every_x_day_subroute').prop("checked", true);
                    $dialogElement.find('#every_x_day__interval').val(parseInt(serie.pattern.interval));
                    break;
                case "daily__every_weekday":
                    $dialogElement.find('#radio_pattern_daily_every_weekday_subroute').prop("checked", true);
                    break;
            }
            break;
        case "weekly":
            $dialogElement.find('#radio_pattern_weekly').prop("checked", true);
            $dialogElement.find("#week_interval").val(serie.pattern.week_interval);

            const days = [
                $dialogElement.find("#monday"),
                $dialogElement.find("#tuesday"),
                $dialogElement.find("#wednesday"),
                $dialogElement.find("#thursday"),
                $dialogElement.find("#friday"),
                $dialogElement.find("#saturday"),
                $dialogElement.find("#sunday"),
            ]

            for (let i = 1; i < 8; i++) {
                if (serie.pattern.days.get(i) === true) {
                    days[i - 1].attr("checked", true);
                }
            }
            break;
        case "monthly":
            $dialogElement.find('#radio_pattern_monthly').prop("checked", true).click();

            switch(serie.pattern.pattern_routine) {
                case "month__every_x_day_every_y_month":
                    $dialogElement.find('#every_x_day_every_y_month__day_of_month_radio').prop("checked", true);
                    $dialogElement.find('#every_x_day_every_y_month__day_of_month').val(serie.pattern.day_of_month);
                    $dialogElement.find('#every_x_day_every_y_month__month_interval').val(serie.pattern.interval);
                    break;
                case "month__every_arbitrary_date_of_month":
                    $dialogElement.find('#every_x_day_every_y_month__month_interval_radio').prop("checked", true);
                    $dialogElement.find("#every_dynamic_date_of_month__arbitrator").attr("init_value", serie.pattern.arbitrator);
                    $dialogElement.find("#every_dynamic_date_of_month__weekday").attr("init_value", serie.pattern.weekday);
                    $dialogElement.find("#every_dynamic_date_of_month__month_interval").val(serie.pattern.interval);
                    break;
            }

            break;
        case "yearly":
            $dialogElement.find('#radio_pattern_yearly').prop("checked", true);
            $dialogElement.find('#pattern_yearly_const__year_interval').val(serie.pattern.year_interval);

            switch(serie.pattern.pattern_routine) {
                case "yearly__every_x_of_month":
                    $dialogElement.find('#every_x_datemonth_of_year_radio').prop("checked", true);
                    $dialogElement.find('#every_x_of_month__date').val(serie.pattern.day_index);
                    $dialogElement.find("#every_x_of_month__month").attr("init_value", serie.pattern.month);
                    break;
                case "yearly__every_arbitrary_weekday_in_month":
                    $dialogElement.find('#every_x_dynamic_day_in_month_radio').prop("checked", true);
                    $dialogElement.find("#every_arbitrary_weekday_in_month__arbitrator").attr("init_value", serie.pattern.arbitrator);
                    $dialogElement.find("#every_arbitrary_weekday_in_month__weekday").attr("init_value", serie.pattern.weekday);
                    $dialogElement.find("#every_arbitrary_weekday_in_month__month").attr("init_value", serie.pattern.month);
                    $dialogElement("#every_arbitrary_weekday_in_month__month").val(serie.pattern.month);
                    break;
            }

            break;
    }

    // This is a bad solution to a pesky bug where the "daily" strategy choices appear when selecting
    // weekly/monthly/yearly. Should be fixed on createSerieDialog when time allows.
    if (serie.pattern.pattern_type !== "daily") {
        $dialogElement.find('#patternRoute_daily').hide();
    }
}

/**
 *
 * @param {*} manifest
 */
export function PopulateCreateSerieDialogFromManifest(manifest, serie_uuid, $dialogElement) {
    console.log("manifest", manifest);
    [
        { to: "#serie_uuid", value: serie_uuid },
        { to: "#serie_title", value: manifest.title },
        { to: "#serie_title_en", value: manifest.title_en },
        { to: "#serie_expected_visitors", value: manifest.expected_visitors },
        { to: "#serie_start", value: manifest.start_time },
        { to: "#serie_end", value: manifest.end_time },
        { to: "#serie_ticket_code", value: manifest.ticket_code },
        { to: "#area_start_date", value: manifest.start_date },
        { to: "#id_meeting_place", value: manifest.meeting_place },
        { to: "#id_meeting_place_en", value: manifest.meeting_place_en },
        { to: "#id_responsible", value: manifest.responsible },
        { to: '#id_status', value: manifest.status },
        { to: '#id_display_text', value: manifest.display_text },
        { to: '#id_display_text_en', value: manifest.display_text_en },
    ].forEach( (mapping) => { $dialogElement.find(mapping.to).val(mapping.value ).trigger('change'); } );

    if (manifest.rooms.length > 0) {
        let roomSelectContext = Object();
        roomSelectContext.rooms = manifest.rooms.map(a => a.id).join(",");
        roomSelectContext.room_name_map = new Map();

        for (let i = 0; i < manifest.rooms.length; i++) {
            let room = manifest.rooms[i];
            roomSelectContext.room_name_map.set(String(room.id), room.name);
        }

        document.dispatchEvent(new CustomEvent(
            "arrangementInspector.d2_roomsSelected",
            { detail: {
                context: roomSelectContext
            } }
        ));
    }
    if (manifest.people.length > 0) {
        let peopleSelectContext = Object();
        peopleSelectContext.people = manifest.people.map(a => a.id).join(",");
        peopleSelectContext.people_name_map = new Map();

        for (let i = 0; i < manifest.people.length; i++) {
            let person = manifest.people[i];
            peopleSelectContext.people_name_map.set(String(person.id), person.name);
        }

        document.dispatchEvent(new CustomEvent(
            "arrangementInspector.d2_peopleSelected",
            { detail: {
                context: peopleSelectContext
            } }
        ));
    }

    manifest.display_layouts.forEach(display_layout => {
        $dialogElement.find('#id_display_layouts_serie_planner_' + display_layout.id)
            .prop( "checked", true );
    })

    switch(manifest.recurrence_strategy) {
        case "StopWithin":
            $dialogElement.find('#radio_timeAreaMethod_stopWithin').prop("checked", true).click();
            $dialogElement.find('#area_stopWithin').val(manifest.stop_within);
            $dialogElement.find('#area_stopWithin').removeAttr("disabled");
            break;
        case "StopAfterXInstances":
            $dialogElement.find('#radio_timeAreaMethod_stopAfterXInstances').prop("checked", true).click();
            $dialogElement.find('#area_stopAfterXInstances').val(manifest.stop_after_x_occurences);
            $dialogElement.find('#area_stopAfterXInstances').removeAttr("disabled");
            break;
        case "NoStopDate":
            $dialogElement.find('#radio_timeAreaMethod_noStopDate').prop("checked", true).click();
            $dialogElement.find('#area_noStop_projectXMonths').val(manifest.project_x_months_into_future);
            $dialogElement.find('#area_noStop_projectXMonths').removeAttr("disabled");
            break;
    }

    switch (manifest.pattern) {
        case "daily":
            $dialogElement.find('#radio_pattern_daily').prop("checked", true).click();

            switch(manifest.pattern_strategy) {
                case "daily__every_x_day":
                    $dialogElement.find('#radio_pattern_daily_every_x_day_subroute').prop("checked", true);
                    $dialogElement.find('#every_x_day__interval').val(parseInt(manifest.strategy_specific.interval));
                    $dialogElement.find('#every_x_day__interval').removeAttr("disabled");
                    break;
                case "daily__every_weekday":
                    $dialogElement.find('#radio_pattern_daily_every_weekday_subroute').prop("checked", true);
                    break;
            }
            break;
        case "weekly":
            $dialogElement.find('#radio_pattern_weekly').prop("checked", true).click();
            $dialogElement.find("#week_interval").val(parseInt(manifest.strategy_specific.interval));

            const days = [
                $dialogElement.find("#monday"),
                $dialogElement.find("#tuesday"),
                $dialogElement.find("#wednesday"),
                $dialogElement.find("#thursday"),
                $dialogElement.find("#friday"),
                $dialogElement.find("#saturday"),
                $dialogElement.find("#sunday"),
            ]

            for (let i = 0; i < manifest.strategy_specific.days.length; i++) {
                if (manifest.strategy_specific.days[i] == true) {
                    days[i].attr("checked", true);
                }
            }

            break;
        case "monthly":
            $dialogElement.find('#radio_pattern_monthly').prop("checked", true).click();
            switch(manifest.pattern_strategy) {
                case "month__every_x_day_every_y_month":
                    $dialogElement.find('#every_x_day_every_y_month__day_of_month_radio').prop("checked", true);
                    $dialogElement.find('#every_x_day_every_y_month__day_of_month').val(manifest.strategy_specific.day_of_month);
                    $dialogElement.find("#every_x_day_every_y_month__month_interval").val(parseInt(manifest.strategy_specific.interval));
                    break;
                case "month__every_arbitrary_date_of_month":
                    $dialogElement.find('#every_x_day_every_y_month__month_interval_radio').prop("checked", true);
                    $dialogElement.find('#every_dynamic_date_of_month__arbitrator').val(manifest.strategy_specific.arbitrator);
                    $dialogElement.find('#every_dynamic_date_of_month__weekday').val(manifest.strategy_specific.day_of_week);
                    $dialogElement.find('#every_dynamic_date_of_month__month_interval').val(manifest.strategy_specific.interval);
                    break;
            }
            break;
        case "yearly":
            $dialogElement.find('#radio_pattern_yearly').prop("checked", true).click();
            $dialogElement.find('#pattern_yearly_const__year_interval').val(manifest.strategy_specific.interval);
            switch(manifest.pattern_strategy) {
                case "yearly__every_x_of_month":
                    $dialogElement.find('#every_x_datemonth_of_year_radio').prop("checked", true);
                    $dialogElement.find('#every_x_of_month__date').val(manifest.strategy_specific.day_of_month);
                    $dialogElement.find('#every_x_of_month__month').val(manifest.strategy_specific.month);
                    break;
                case "yearly__every_arbitrary_weekday_in_month":
                    $dialogElement.find('#every_x_dynamic_day_in_month_radio').prop("checked", true);
                    $dialogElement.find('#every_arbitrary_weekday_in_month__arbitrator').val(manifest.strategy_specific.arbitrator);
                    $dialogElement.find('#every_arbitrary_weekday_in_month__weekday').val(manifest.strategy_specific.day_of_week);
                    $dialogElement.find('#every_arbitrary_weekday_in_month__month').val(manifest.strategy_specific.month);
                    break;
            }

            break;
    }

    if (manifest.pattern !== "daily") {
        $dialogElement.find('#patternRoute_daily').hide();
    }
}

/**
 *
 * @param {*} event
 */
export function PopulateCreateEventDialog(event, $dialogElement) {
    let parseDateOrStringToArtifacts = function (dateOrString) {
        if (dateOrString instanceof String)
            return Utils.splitStrDate(dateOrString);
        else if (dateOrString instanceof Date)
            return Utils.splitDateIntoDateAndTimeStrings(event.start);
        else throw "Invalid value or type"
    }

    console.log(event);

    let [fromDate, fromTime]    = parseDateOrStringToArtifacts(event.start);
    let [toDate, toTime]        = parseDateOrStringToArtifacts(event.end);

    [
        { target: "#event_uuid", value: event._uuid },
        { target: "#title", value: event.title },
        { target: "#title_en", value: event.title_en },
        { target: "#ticket_code", value: event.ticket_code },
        { target: '#expected_visitors', value: event.expected_visitors },
        { target: '#fromDate', value: fromDate },
        { target: '#fromTime', value: fromTime },
        { target: '#toDate', value: toDate },
        { target: '#toTime', value: toTime },
        { target: '#buffer_before_start', value: event.before_buffer_start },
        { target: '#buffer_before_end', value: event.before_buffer_end },
        { target: '#buffer_after_start', value: event.after_buffer_start },
        { target: '#buffer_after_end', value: event.after_buffer_end },
        { target: '#_backingAudienceId', value: event.audience },
        { target: '#_backingArrangementTypeId', value: event.arrangement_type },
        { target: '#id_meeting_place', value: event.meeting_place },
        { target: '#id_meeting_place_en', value: event.meeting_place_en },
        { target: '#id_status', value: event.status },
        { target: '#id_responsible', value: event.responsible },
    ].forEach( (mapping) => {
        $dialogElement.find( mapping.target ).val( mapping.value );
    } )


    if (Array.isArray(event.display_layouts)) {
        event.display_layouts.forEach(element => {
            $dialogElement.find(`#${String(parseInt(element))}_dlcheck`)
                .prop( "checked", true );
        })
    }
    else {
        throw "Display layouts must be an array";
    }

    // This is fairly messy I am afraid, but the gist of what we're doing here is simulating that the user
    // has "selected" rooms as they would through the dialog interface.
    if (event.people.length > 0) {
        var peopleSelectContext = Object();
        peopleSelectContext.people = event.people.join(",");
        peopleSelectContext.people_name_map = event.people_name_map;
        document.dispatchEvent(new CustomEvent(
            "arrangementCreator.d1_peopleSelected",
            { detail: {
                context: peopleSelectContext
            } }
        ));
    }
    if (event.rooms.length > 0) {
        var roomSelectContext = Object();
        roomSelectContext.rooms = event.rooms.join(",");
        roomSelectContext.room_name_map = event.room_name_map;
        document.dispatchEvent(new CustomEvent(
            "arrangementCreator.d1_roomsSelected",
            { detail: {
                context: roomSelectContext
            } }
        ));
    }
}
