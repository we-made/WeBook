class LinkedHTMLElement extends HTMLElement {
    constructor() {
        super();

        this.attachShadow({ mode: 'open' });

        const baseStylesheetLinkElement = document.createElement("link");
        baseStylesheetLinkElement.setAttribute("rel", "stylesheet");
        baseStylesheetLinkElement.setAttribute("href", "/static/css/base.css");

        const mdbStylesheetLinkElement = document.createElement("link");
        mdbStylesheetLinkElement.setAttribute("rel", "stylesheet");
        mdbStylesheetLinkElement.setAttribute("href", window.sharedUrls.mdb);

        this.shadowRoot.append(mdbStylesheetLinkElement, 
                               baseStylesheetLinkElement, );
    }
}


class SelectedPill extends LinkedHTMLElement {
    /**
     * Component: SelectedPill
     * 
     */
    constructor() {
        super()
    
        const wrapper = document.createElement("span");
        wrapper.classList.add("wb-bg-secondary", "rounded-pill", "p-3",);

        const textSpan = document.createElement("span");
        textSpan.innerText = this.getAttribute("name"); 
        textSpan.setAttribute("id", this.getAttribute("id"));
        wrapper.appendChild(textSpan);
        
        const timesLink = document.createElement("a");
        timesLink.setAttribute("href", "#");
        timesLink.classList.add("text-danger", "ms-3", "fw-bold");
        timesLink.innerHTML = "X";
        
        const d_trigger = this.getAttribute("d-trigger");
        if (d_trigger !== null) {
            timesLink.setAttribute("d-trigger", d_trigger);
        }
        if (this.onclick !== null) {
            timesLink.onclick = this.onclick;
        }

        wrapper.appendChild(timesLink);

        this.shadowRoot.append(wrapper);
    }
}

class ActivitySummaryLineElement extends LinkedHTMLElement {
    constructor () {
        super();

        const values = {
            title:      this.getAttribute("title"),
            startDate:  this.getAttribute("startDate"),
            startTime:  this.getAttribute("startTime"),
            endDate:    this.getAttribute("endDate"),
            endTime:    this.getAttribute("endTime")
        };

        const baseStylesheetLinkElement = document.createElement("link");
        baseStylesheetLinkElement.setAttribute("rel", "stylesheet");
        baseStylesheetLinkElement.setAttribute("href", "/static/css/base.css");

        const mdbStylesheetLinkElement = document.createElement("link");
        mdbStylesheetLinkElement.setAttribute("rel", "stylesheet");
        mdbStylesheetLinkElement.setAttribute("href", window.sharedUrls.mdb);

        const lineElement = document.createElement("div");
        lineElement.classList.add("bg-white", "p-3", "mt-2", "rounded-pill");
        
        const titleSpan = document.createElement("span");
        titleSpan.innerText = `${values.startDate} / ${values.endDate}`;

        const actionsSpan = document.createElement("span");
        actionsSpa

        lineElement.append(titleSpan);
        
        this.shadowRoot.append(lineElement);
    }
}

customElements.define('selected-pill', SelectedPill);
customElements.define("activity-summary-line", ActivitySummaryLineElement);