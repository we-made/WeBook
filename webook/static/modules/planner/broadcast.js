class Recipient {
    constructor(name) {
        this.name = name;
        this._messages = new Map();
    }

    leaveMessage(messageKey, message) {
        if (!messageKey)
            messageKey = crypto.randomUUID();

        this._messages.set(messageKey, message);
    }

    getMessage(messageKey) {
        return this._messages.get(messageKey);
    }

    allMessages() {
        return Array.from(this._messages.values());
    }

    clear() {
        this._messages = [];
    }
}

export class MessagesFacility {
    constructor() {
        this._recipients = new Map();
        this._subscriptions = new Map();
    }

    send(recipient, payload, key=undefined) {
        if (!this._recipients.has(recipient))
            this._recipients.set(recipient, new Recipient(recipient));
        
        this._recipients.get(recipient).leaveMessage(key, payload);
        
        if (this._subscriptions.get(recipient))
            this._subscriptions.get(recipient).forEach((subscriptionFunction) => { subscriptionFunction(key, payload) });
    }

    addressedTo(recipient) {
        return this._recipients.get(recipient);
    }

    subscribe( recipient, onChange ) {
        if (this._subscriptions.has( recipient ))
            this._subscriptions.get( recipient ).push( onChange );
        else
            this._subscriptions.set( recipient, [ onChange ] );
    }
}