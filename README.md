# Linen Locale

Synthetic notification catalogs for a linen supply cooperative. Each catalog
uses one key=value record per line. English defines the required keys and
named substitution fields. Translated text can reorder substitution fields,
but it must keep their names and occurrence counts.

The planned French wording update changes the pickup, late-return and invoice
messages. Before merging, reviewers need line-specific feedback and proof
that the unchanged Spanish catalog stayed outside the normal changed scope.


###clipboard
pickup_ready=La commande {order} est disponible à {depot}.
dropoff_window=Retour à {depot} entre {start} et {end}.
late_return=La commande {order} a {days} jours de retard.
stock_arrived={count} lots sont arrivés à {depot}.
order_cancelled=La commande {order} a été annulée.
invoice_ready=La facture {invoice} est due le {date}.
route_delay=La tournée {route} a {minutes} minutes de retard.
shortage=Il manque {count} lots dans la commande {order}.
temperature=Le dépôt {depot} a relevé {value} degrés.
exception_closed=Le dossier {case} a été clôturé par {agent}.
handover={driver} a remis la commande {order} à {receiver}.
return_complete=La commande {order} a été rendue à {depot}.
