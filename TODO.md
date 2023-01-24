Offer to sell
1. User posts listing with price
2. Buyer buys listing

Request to buy
1. Buyer posts listing with request price
2. Seller clicks Accept. A copy of the Listing is entered into the DB. However, three things change: (1) listing_type changes from Request To Buy to Offer To Sell; (2) seller becomes buyer; (3) buyer becomes seller. This creates a payment request and email (and SMS) notification to the buyer to pay (this email includes a link to this new listing). 

[ ] Check if payment requests are still going into accounts linked to Stripe Connect or if it is only working for class Listing at the moment

[ ] Ads

[ ] Ads upon searches

For delivery:
[ ] Add edit and delete for the ones that request.user made
[ ] Only allow request.user to accept deliveries from other other 

[ ] Make it so that only Stripe Connect-connected users can transact; it is too much of a pain to use Venmo 

[ ] Email on lottery winner and on sales and notifications in site



[ ] Emails (upon sale and purchase; upon delivery
[ ] In-site notifications
[ ] Customer service — form that sends to me on site
[x] Request to buy (in addition to offer to sell)

Emails upon:
[ ] Purchase
[ ] Sale
[ ] Request to group member for payment
[ ] Winning lottery
[ ] Referral used

[ ] Create separate CreateViews for [ ] general advertisement and [ ] listing (in which pass within the URL parameters the Listing.id itself so that it is automatically saved to the model from the form_valid() function and also remember to also pass the Listing.title within the header).

[ ] Ability to purchase ads. Make sure that the payments go directly to your centralized Stripe account.

[ ] Almeida
[ ] Rossi
[ ] Rossetti
[ ] Dong




