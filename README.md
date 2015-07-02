# stash

RESTful API for managing limited inventory of homogeneous items, e.g., I have
10 tickets for an event and I am not allowed to oversell.

## High Level Overview

Stash has two resources: items and reservations.  Reservations are
nested under items.

### Items
 - View an index of items: `GET /items`
 - View the details of a specific item: `GET /items/<id>`
 - Update an item: `PUT /items/<id>`
 - Remove an item: `DELETE /items/<id>`

### Reservations
 - View an index of reservations: `GET /reservations`
 - View an index of reservations on behalf of a specific item: 
   `GET /items/<id>/reservations`
 - View the details of a specific reservation: `GET /reservations/<id>` or 
   `GET /items/<id>/reservations/<id>`
 - Commit a reservation: `PUT /reservations/<id>` or 
   `PUT /items/<id>/reservations/<id>`
 - Cancel a reservation: `DELETE /reservations/<id>`

## Detailed Walk-through

Let's see what items are available.

```
GET /items
```

```
200 OK
[]
```

Hmm, looks like nothing's there.

Let's provision some inventory:

```
POST /items
{
  "metadata": {
    "name": "bday party",
    "ticket_class": "GA"
  },
  "tags": ["event"],
  "capacity": 10
}
```

```
201 Created
{
  "id": "iGvBWVcAv7s6MkSHRDdpo4",
  "href": "/items/iGvBWVcAv7s6MkSHRDdpo4",
  "metadata": {
    "name": "bday party",
    "ticket_class": "GA"
  },
  "tags": ["event"],
  "capacity": 10,
  "available": 10,
  "committed": 0,
  "links": {
    "reservations": /items/iGvBWVcAv7s6MkSHRDdpo4/reservations"
  }
}
```

Cool, now let's see if we can find the event:

```
GET /items?tags[contains]=event&metadata.ticket_class=GA
```

```
200 OK
[
  "/items/iGvBWVcAv7s6MkSHRDdpo4"
]
```

Hot dang, there's the event we created. Let's check it out:

```
GET /items/iGvBWVcAv7s6MkSHRDdpo4
```

```
200 OK
{
  "id": "iGvBWVcAv7s6MkSHRDdpo4",
  "href": "/items/iGvBWVcAv7s6MkSHRDdpo4",
  "metadata": {
    "name": "bday party",
    "ticket_class": "GA"
  },
  "tags": ["event"],
  "capacity": 10,
  "available": 10,
  "committed": 0,
  "links": {
    "reservations": /items/iGvBWVcAv7s6MkSHRDdpo4/reservations"
  }
}
```

Awesome, now let's reserve some inventory:

```
POST /items/iGvBWVcAv7s6MkSHRDdpo4/reservations
{
  "quantity": 2
}
```

```
201 Created
{
  "id": "d4PM897XVd9PTRx6xFN8qH",
  "href": "/items/iGvBWVcAv7s6MkSHRDdpo4/reservations/d4PM897XVd9PTRx6xFN8qH",
  "status": "pending",
  "expires_at": "2019-06-30T23:22:59.525178Z",
  "quantity": 2
}
```

We just created our first reservation. Even though the reservation is not 
committed, it decrements the available inventory. By default the reservation 
will expire unless we commit it, like this:

```
PUT /items/iGvBWVcAv7s6MkSHRDdpo4/reservations/d4PM897XVd9PTRx6xFN8qH
{
  "status": "committed"
}
```

```
200 OK
```

After committing the inventory, it will increment the committed tally for the 
item class.

If we want unlock the inventory for a reservation, simply delete the 
reservation:

```
DELETE /items/iGvBWVcAv7s6MkSHRDdpo4/reservations/d4PM897XVd9PTRx6xFN8qH
```

```
200 OK
```

That will increment the available inventory which had previously been 
decremented by the reservation.
