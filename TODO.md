Offer to sell
1. User posts listing with price
2. Buyer buys listing

Request to buy
1. Buyer posts listing with request price
2. Seller clicks Accept. A copy of the Listing is entered into the DB. However, three things change: (1) listing_type changes from Request To Buy to Offer To Sell; (2) seller becomes buyer; (3) buyer becomes seller. This creates a payment request and email (and SMS) notification to the buyer to pay (this email includes a link to this new listing). 

[ ] Check if payment requests are still going into accounts linked to Stripe Connect or if it is only working for class Listing at the moment

[ ] Ads

[ ] Ads upon searches