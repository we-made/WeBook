export function PopulateCreateSerieDialogFromSerie(serie, $dialogElement) {
    if (serie === undefined) {
        console.error("Serie is undefined", serie);
        debugger;
    }

    $dialogElement.find('#serie_uuid').val(serie._uuid);
    $dialogElement.find('#serie_title').val(serie.time.title);
    $dialogElement.find('#serie_title_en').val(serie.time.title_en);
    $dialogElement.find('#serie_start').val(serie.time.start).change();
    $dialogElement.find('#serie_end').val(serie.time.end).change();
    $dialogElement.find('#serie_ticket_code').val(serie.time.ticket_code);
    $dialogElement.find('#serie_expected_visitors').val(serie.time.expected_visitors);
    $dialogElement.find('#area_start_date').val(serie.time_area.start_date);
    $dialogElement.find('#buffer_before_start').val(serie.buffer.before?.start);
    $dialogElement.find('#buffer_before_end').val(serie.buffer.before?.end);
    $dialogElement.find('#buffer_after_start').val(serie.buffer.after?.start);
    $dialogElement.find('#buffer_after_end').val(serie.buffer.after?.end);

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
    $dialogElement.find('#serie_uuid')?.attr("value", serie_uuid);
    $dialogElement.find('#serie_title')?.val(manifest.title);
    $dialogElement.find('#serie_title_en')?.attr("value", manifest.title_en);
    $dialogElement.find('#serie_expected_visitors')?.attr("value", manifest.expected_visitors);
    $dialogElement.find('#serie_ticket_code')?.attr("value", manifest.ticket_code);
    $dialogElement.find('#area_start_date')?.attr("value", manifest.start_date);
    $dialogElement.find('#serie_start')?.val(manifest.start_time).change();
    $dialogElement.find('#serie_end')?.val(manifest.end_time).change();

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

    let [fromDate, fromTime]    = parseDateOrStringToArtifacts(event.start);
    let [toDate, toTime]        = parseDateOrStringToArtifacts(event.end);

    $dialogElement.find('#event_uuid').val(event._uuid);
    $dialogElement.find('#title').val(event.title);
    $dialogElement.find('#title_en').val(event.title_en);
    $dialogElement.find('#ticket_code').val(event.ticket_code);
    $dialogElement.find('#expected_visitors').val(event.expected_visitors);
    $dialogElement.find('#fromDate').val(fromDate);
    $dialogElement.find('#fromTime').val(fromTime);
    $dialogElement.find('#toDate').val(toDate);
    $dialogElement.find('#toTime').val(toTime);
    $dialogElement.find('#buffer_before_start').val(event.before_buffer_start);
    $dialogElement.find('#buffer_before_end').val(event.before_buffer_end);
    $dialogElement.find('#buffer_after_start').val(event.after_buffer_start);
    $dialogElement.find('#buffer_after_end').val(event.after_buffer_end);

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
