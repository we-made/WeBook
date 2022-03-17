

export class ArrangementInspector {
    constructor () {
    }

    inspectArrangement( arrangement ) {
        this._flush();
        this._injectDialog(arrangement);
        this._spawnDialog();
    }

    _flush() {
        $("#dialog").remove();
    }

    _injectDialog(arrangement) {
        $('body').append(this._fabricateDialog(arrangement));
    }

    _spawnDialog() {
        let innerCalendar = new FullCalendar.Calendar(document.getElementById('innerCalendar'), {
            initialView: "listMonth",
            events: [
                { title: "My Supreme Event", start: "17.03.2022 09:00", end: "17.03.2022 15:00" }
            ]
        })

        $( function() {
            $( "#tabs" ).tabs();
          } );
        $(function() {
            $( "#dialog" ).dialog({  height: 400, width: 600});
        });        
        innerCalendar.render();
    }

    _fabricateDialog(arrangement) {
        return `
            <div id="dialog" title="${arrangement.name}">
  
                <div class='clearfix'>
                    <div class="float-start">
                        <select class='form-control rounded-0 rounded-top-1'>
                            <option value='0'>Main Planner</option>
                        </select>
                    </div>

                    <div class='btn btn-group p-0 shadow-0 rounded-0 float-end square' style='border-bottom-left-radius: 0px; border-bottom-right-radius: 0px;'>
                        <a class='btn btn-light rounded-0 rounded-top-1'>
                            <i class='fas fa-edit'></i>
                            Rediger
                        </a>
                        <a class='btn btn-light rounded-0 rounded-top-1'>
                            <i class='fas fa-archive'></i>
                            Arkiver
                        </a>
                    </div>
                </div>

                <div id="tabs">
                    <ul>
                        <li><a href="#tabs-1">Informasjon</a></li>
                        <li><a href="#tabs-2">Aktiviteter</a></li>
                        <li><a href="#tabs-2">Notater</a></li>
                        <li><a href="#tabs-3">Kvitteringer</a></li>
                    </ul>
                    <div id="tabs-1">
                        <table class='table table-sm'>
                            <tbody>
                                <tr>
                                    <th><strong>Navn:</strong> <input type='text' class='form-control' /> </th>
                                </tr>
                                <tr>
                                    <th>
                                        <strong>Vises i multimedia guide:</strong> 
                                        <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" role="switch" id="flexSwitchCheckChecked" checked />
                                        <label class="form-check-label" for="flexSwitchCheckChecked">Checked switch checkbox input</label>
                                      </div>
                                    </th>
                                </tr>
                                <tr>
                                    <td>
                                        <strong>Målgruppe:</strong>
                                        <select class='form-control'>
                                            
                                        </select>
                                    </td>
                                </tr>
                                <tr>
                                    <td><button class="btn btn-sm btn-light btn-block btn-success">Lagre endringer</btn></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div id="tabs-2">
                        <div id='innerCalendar'></div>
                    </div>
                    <div id="tabs-3">
                        
                    </div>
                </div>
            </div>
            `;
    }
}