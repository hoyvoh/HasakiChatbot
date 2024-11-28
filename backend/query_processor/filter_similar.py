from Levenshtein import distance
from collections import defaultdict
from bson import ObjectId

def filter_similar_products(products, threshold=0.9):
    def calculate_similarity(title1, title2):
        max_len = max(len(title1), len(title2))
        if max_len == 0:
            return 1.0  # If both titles are empty
        levenshtein_dist = distance(title1, title2)
        return 1 - (levenshtein_dist / max_len)

    schemes = []
    used_indices = set()

    for i, product in enumerate(products):
        if i in used_indices:
            continue
        
        current_scheme = [product]
        used_indices.add(i)
        
        for j in range(i + 1, len(products)):
            if j in used_indices:
                continue
            
            similarity = calculate_similarity(product['pname'], products[j]['pname'])
            if similarity < threshold:  # Not too similar
                current_scheme.append(products[j])
                used_indices.add(j)

        schemes.append({'products': current_scheme})  # Store scheme in specified format
        if len(schemes) >= 3:  # Limit to 3 schemes
            break

    return schemes

# Example input
products = [
    {'_id': ObjectId('673f71d5154242d7bd8176b2'), 'plink': 'https://hasaki.vn/san-pham/son-kem-li-3ce-mau-do-cam-child-like-4g-35130.html', 'pname': 'Son Kem Lì 3CE Mịn Màng Như Nhung Child Like - Đỏ Cam 4g', 'price': 277000, 'rating': 2.8},
    {'_id': ObjectId('673f71d5154242d7bd817715'), 'plink': 'https://hasaki.vn/san-pham/son-kem-sieu-li-3ce-macaron-red-mau-do-tuoi-4g-99031.html', 'pname': 'Son Kem Lì 3CE Mịn Nhẹ Macaron Red - Đỏ Tươi 4g', 'price': 277000, 'rating': 1.0},
    {'_id': ObjectId('673f71d5154242d7bd817733'), 'plink': 'https://hasaki.vn/san-pham/son-kem-sieu-li-3ce-live-a-little-mau-do-dat-4g-99035.html', 'pname': 'Son Kem Lì 3CE Mịn Nhẹ Live A Little - Đỏ Đất 4g', 'price': 277000, 'rating': 1.0},
    {'_id': ObjectId('673f71d5154242d7bd817746'), 'plink': 'https://hasaki.vn/san-pham/son-kem-sieu-li-3ce-needful-mau-do-gach-4g-99029.html', 'pname': 'Son Kem Lì 3CE Mịn Nhẹ Needful - Đỏ Gạch 4g', 'price': 277000, 'rating': 1.0},
    {'_id': ObjectId('673f71d7154242d7bd8179c9'), 'plink': 'https://hasaki.vn/san-pham/son-kem-sieu-li-3ce-peach-tease-mau-cam-san-ho-4g-99027.html', 'pname': 'Son Kem Lì 3CE Mịn Nhẹ Peach Tease - Cam San Hô 4g', 'price': 277000, 'rating': 1.0},
    {'_id': ObjectId('673f71d7154242d7bd8179e3'), 'plink': 'https://hasaki.vn/san-pham/son-kem-sieu-li-3ce-immanence-mau-do-tram-4g-99033.html', 'pname': 'Son Kem Lì 3CE Mịn Nhẹ Immanence - Đỏ Trầm 4g', 'price': 277000, 'rating': 1.0},
    {'_id': ObjectId('673f71d8154242d7bd817abd'), 'plink': 'https://hasaki.vn/san-pham/son-kem-b-o-m-02-bff-mau-do-cam-4g-88461.html', 'pname': 'Son Kem B.O.M #02 BFF - Đỏ Cam 4g', 'price': 149000, 'rating': 5.0},
    {'_id': ObjectId('673f71d8154242d7bd817ac0'), 'plink': 'https://hasaki.vn/san-pham/son-kem-li-colorkey-o316-hong-cam-18g-117313.html', 'pname': 'Son Kem Lì Colorkey O316 Hồng Cam 1.8g', 'price': 131000, 'rating': 5.0},
    {'_id': ObjectId('673f71d8154242d7bd817ae3'), 'plink': 'https://hasaki.vn/san-pham/son-kem-perfect-diary-mau-904-25g-114993.html', 'pname': 'Son Kem Perfect Diary 904 Màu Đỏ Cam 2.5g', 'price': 76000, 'rating': 5.0},
    {'_id': ObjectId('673f71d9154242d7bd817b0b'), 'plink': 'https://hasaki.vn/san-pham/son-kem-silkygirl-tuoi-mong-lau-troi-07-cam-ngot-4-5g-128836.html', 'pname': 'Son Kem Silkygirl Tươi Mọng Lâu Trôi - 07 Cam Ngọt 4.5g', 'price': 99000, 'rating': 0.0},
]

# schemes = filter_similar_products(products, threshold=0.5)

# # Print the output schemes
# for index, scheme in enumerate(schemes):
#     print(f"Scheme {index + 1}: {scheme}")
