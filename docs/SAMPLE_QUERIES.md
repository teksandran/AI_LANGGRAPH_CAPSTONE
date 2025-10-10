# Sample Queries for Beauty & Aesthetics Multi-Agent System

This document provides comprehensive query examples for testing the BeautySearchAgent system.

---

## 🎯 Query Categories

The system has two specialized agents:
1. **ProductAgent** - Handles product information (Botox, Evolus, aesthetic treatments)
2. **BusinessAgent** - Handles business searches (salons, spas, clinics via Yelp API)

The **SupervisorAgent** automatically routes your query to the right agent!

---

## 💉 ProductAgent Queries (RAG-based Product Information)

### Basic Product Information

```
What is Botox?
Tell me about Botox
Explain how Botox works
What is Evolus?
What is Jeuveau?
Tell me about Botox Cosmetic
How does Botox work for wrinkles?
```

### Treatment Areas & Uses

```
What areas can be treated with Botox?
Where can I use Botox on my face?
What facial areas does Botox treat?
What are Botox indications?
What is Botox approved for?
Can Botox treat forehead lines?
Does Botox work on crow's feet?
What are the treatment areas for Evolus?
```

### Benefits & Effects

```
What are the benefits of Botox?
What results can I expect from Botox?
How long do Botox results last?
What are the effects of Botox?
What are the advantages of using Botox?
Why should I choose Botox?
```

### Product Comparisons

```
Compare Botox and Evolus
What's the difference between Botox and Evolus?
Botox vs Evolus
Which is better: Botox or Jeuveau?
Compare Botox and Jeuveau
How does Evolus compare to Botox?
What are the similarities between Botox and Evolus?
Botox or Evolus for forehead lines?
```

### Product Types & Categories

```
What type of product is Botox?
Is Botox a neurotoxin?
What category does Evolus fall under?
What kind of injectable is Botox?
Is Jeuveau a dermal filler?
What are injectable neurotoxins?
```

### Safety & Approval

```
Is Botox FDA approved?
Is Evolus FDA approved?
Is Botox safe?
What are Botox contraindications?
Who should not use Botox?
```

### Duration & Maintenance

```
How long does Botox last?
When will I see Botox results?
How often should I get Botox?
How frequently do I need Botox treatments?
```

### Advanced Product Queries

```
What is the active ingredient in Botox?
How is Botox administered?
What is the mechanism of action for Botox?
How does Botox reduce wrinkles?
What is botulinum toxin type A?
```

---

## 🏢 BusinessAgent Queries (Yelp-based Business Search)

### General Beauty Services

```
Find beauty salons near me
Show me beauty salons in Los Angeles
Find spas in New York
Where can I get beauty treatments in San Francisco?
Best beauty salons in Chicago
Top-rated spas near Boston
```

### Specific Service Searches

```
Find Botox clinics in New York
Where can I get Botox in Los Angeles?
Botox providers in Miami
Find aesthetic clinics in San Diego
Medical spas near San Francisco
Find dermatologists in Seattle
```

### Location-Specific Searches

```
Beauty salons in Manhattan
Spas in Beverly Hills
Hair salons in Brooklyn
Nail salons in Queens
Massage spas in Santa Monica
Aesthetic clinics in West Hollywood
```

### Service Type Searches

```
Find facial spas in Dallas
Massage therapy in Austin
Nail salons in Houston
Hair styling in Phoenix
Eyelash extensions in Denver
Skin care clinics in Portland
```

### Quality-Based Searches

```
Best rated spas in Chicago
Top beauty salons in Miami
Highest rated Botox clinics in NYC
Best medical spas in LA
Top aesthetic clinics in San Francisco
Most reviewed salons in Boston
```

### Specific Beauty Services

```
Find places for Botox injections in New York
Where can I get facials in Los Angeles?
Manicure and pedicure in San Diego
Hair coloring salons in Seattle
Waxing services in Miami
Makeup artists in Chicago
```

### Medical Aesthetics

```
Find aesthetic medicine clinics in NYC
Medical spas offering Botox in LA
Cosmetic dermatology in San Francisco
Aesthetic injectors in Miami
Non-surgical facial treatments in Boston
Anti-aging clinics in Seattle
```

### Combination Queries

```
Find top-rated Botox clinics in New York with good reviews
Best medical spas in Los Angeles for facial treatments
Affordable beauty salons in Chicago near downtown
Luxury spas in Miami Beach
Full-service beauty salons in San Francisco
```

---

## 🔄 Hybrid Queries (Tests Routing Intelligence)

These queries test the SupervisorAgent's ability to route correctly:

### Should Route to ProductAgent:

```
What are the benefits of Botox for anti-aging?
Tell me about injectable neurotoxins
Explain the difference between Botox and fillers
What products are available for wrinkle reduction?
```

### Should Route to BusinessAgent:

```
I need a Botox appointment in New York
Find me a good aesthetic clinic nearby
Where can I get beauty treatments in my area?
Show me salons that offer Botox
```

### Ambiguous (Tests Intelligence):

```
I want Botox information and where to get it
Tell me about Botox and find clinics in LA
What is Botox and where can I find providers?
```

---

## 📍 City-Specific Query Templates

Replace `{city}` with any major US city:

### Template Queries:

```
Find beauty salons in {city}
Best spas in {city}
Botox clinics in {city}
Medical spas near {city}
Top-rated aesthetic clinics in {city}
Hair salons in downtown {city}
Nail salons in {city}
Massage therapy in {city}
Facial treatments in {city}
Eyelash services in {city}
```

### Popular Cities to Try:

- New York, NY / NYC / Manhattan
- Los Angeles, CA / LA
- San Francisco, CA
- Chicago, IL
- Miami, FL / Miami Beach
- Boston, MA
- Seattle, WA
- Austin, TX
- Portland, OR
- Denver, CO
- San Diego, CA
- Las Vegas, NV
- Dallas, TX
- Houston, TX
- Phoenix, AZ

---

## 🎨 Quick Test Queries

### Quick ProductAgent Tests (30 seconds):

```
1. What is Botox?
2. Compare Botox and Evolus
3. What are Botox treatment areas?
4. How long does Botox last?
5. Is Botox FDA approved?
```

### Quick BusinessAgent Tests (30 seconds):

```
1. Find beauty salons in New York
2. Best spas in Los Angeles
3. Botox clinics in Miami
4. Medical spas in Chicago
5. Hair salons in San Francisco
```

---

## 🧪 Advanced Testing Queries

### Edge Cases:

```
botox (lowercase)
BOTOX (uppercase)
What's botox? (casual)
Tell me everything about Botox (broad)
Botox? (single word question)
Find salons (no location)
Best spa (ambiguous)
New York salons (location first)
```

### Multi-Intent Queries:

```
What is Botox and where can I get it in NYC?
Tell me about Evolus and find providers in LA
Compare Botox vs Evolus and show me clinics
I want to learn about Botox then book an appointment
```

### Conversational Queries:

```
Hey, what's Botox all about?
Can you tell me about aesthetic treatments?
I'm interested in reducing wrinkles, what are my options?
Looking for a good spa in my area
Need recommendations for beauty services
```

---

## 📊 Testing Recommendations

### For Complete System Testing:

1. **Start with Product Queries** (test RAG system):
   - Ask 3-5 product information questions
   - Test comparisons
   - Verify detailed responses

2. **Test Business Searches** (test Yelp integration):
   - Try different cities
   - Test various service types
   - Check for business details (ratings, addresses)

3. **Test Routing Intelligence**:
   - Mix product and business queries
   - Use ambiguous queries
   - Verify correct agent selection

4. **Test Edge Cases**:
   - Misspellings
   - Partial queries
   - Very long queries
   - Single-word queries

---

## 🎯 Query Examples by Use Case

### Use Case 1: New User Learning About Products

```
1. What is Botox?
2. What are the benefits of Botox?
3. Is Botox safe?
4. Compare Botox and Evolus
5. What areas can Botox treat?
```

### Use Case 2: User Looking for Service Provider

```
1. Find Botox clinics in [city]
2. Show me top-rated medical spas in [city]
3. Where can I get Botox near me?
4. Best aesthetic clinics in [city]
5. Find providers with good reviews
```

### Use Case 3: Comprehensive Research

```
1. What is Botox and how does it work?
2. What are all the FDA-approved uses?
3. Compare Botox to other similar products
4. What are the benefits and risks?
5. Find certified providers in my area
```

### Use Case 4: Quick Booking Intent

```
1. Find Botox clinics in New York
2. Show me places with high ratings
3. Which ones are open now?
4. Best reviewed clinics near me
```

---

## 🔧 API Testing Commands

### Using cURL:

```bash
# Product Query
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Botox?"}'

# Business Query
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Find beauty salons in New York"}'

# Comparison Query
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Compare Botox and Evolus"}'

# Direct Product Query
curl -X POST http://localhost:5000/api/product-query \
  -H "Content-Type: application/json" \
  -d '{"query": "Botox benefits", "brand": "botox"}'

# Direct Business Query
curl -X POST http://localhost:5000/api/business-query \
  -H "Content-Type: application/json" \
  -d '{"query": "Find spas", "location": "Los Angeles"}'
```

---

## 💡 Tips for Best Results

### ProductAgent Queries:
- Be specific about what you want to know
- Mention product names explicitly (Botox, Evolus, Jeuveau)
- Ask about specific aspects (benefits, uses, treatment areas)
- Use comparison keywords for side-by-side analysis

### BusinessAgent Queries:
- Always include a location (city, state, or "near me")
- Specify the type of service you're looking for
- Use quality indicators (best, top-rated, highly reviewed)
- Be specific about the service type (spa, salon, clinic)

### General Tips:
- Natural language works! Ask questions as you would to a person
- The system understands context and variations
- You can combine product and business questions
- More specific queries = better results

---

## 📈 Expected Response Times

- **Product Queries (First Time)**: 30-60 seconds (indexing websites)
- **Product Queries (After Indexing)**: 2-5 seconds
- **Business Queries**: 3-8 seconds (Yelp API)
- **Comparison Queries**: 5-10 seconds

---

## 🎉 Ready to Test!

Copy any query from above and paste it into your React app or use cURL to test the API directly.

**Happy Testing!** 🚀
