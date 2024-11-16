from itertools import combinations

data = {
    "budget":43,
    "products":{'p1': 10, 'p2': 15, 'p3': 20, 'p4': 25, 'p5': 30}
}

def suggest_based_on_budget(data, tolerance=0.1, top_n=3):
    budget = data["budget"]
    products = data["products"] #.split(',').strip()
    lower_bound = budget*(1-tolerance)
    upper_bound = budget*(1+tolerance)

    all_solutions = []
    for r in range(1, len(products)+1):
        all_solutions.extend(combinations(products.items(), r))

    legit_solutions = [combo for combo in all_solutions if lower_bound <= sum(price for _,price in combo) <= upper_bound]
    ranked_solutions = sorted(
        legit_solutions,
        key=lambda plan: (
            abs(budget - sum(price for _, price in plan)),  
            -sum(price for _, price in plan),               
            -len(plan)                                      
        )
    )

    top_solutions = [
        (
            [prod[0] for prod in plan],       
            sum(price for _, price in plan)     
        )
        for plan in ranked_solutions[:top_n]
    ]
    return top_solutions

if __name__ == '__main__':
    print(suggest_based_on_budget(data=data))
