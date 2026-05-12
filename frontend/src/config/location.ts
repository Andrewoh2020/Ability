const countries = [
  "United States",
  "United Kingdom",
  "Canada",
  "Australia",
  "Germany",
  "France",
  "Japan",
  "China",
  "India",
  "Brazil",
  "Mexico",
  "Italy",
  "Spain",
  "South Korea",
  "Saudi Arabia",
  "United Arab Emirates",
  "Singapore",
  "Malaysia",
  "Thailand",
  "Vietnam",
  "Philippines",
  "Indonesia"
];

const cities = {
  "United States": [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
    "Austin", "Jacksonville", "Fort Worth", "Columbus", "Charlotte",
    "San Francisco", "Indianapolis", "Seattle", "Denver", "Washington"
  ],
  "United Kingdom": [
    "London", "Manchester", "Birmingham", "Liverpool", "Glasgow",
    "Edinburgh", "Bristol", "Leeds", "Sheffield", "Newcastle",
    "Cardiff", "Belfast", "Nottingham", "Southampton", "Portsmouth",
    "Brighton", "Leicester", "Coventry", "Reading", "Plymouth"
  ],
  "Canada": [
    "Toronto", "Montreal", "Vancouver", "Calgary", "Edmonton",
    "Ottawa", "Winnipeg", "Quebec City", "Hamilton", "Kitchener",
    "London", "Victoria", "Halifax", "Oshawa", "Windsor",
    "Saskatoon", "Regina", "St. John\"s", "Barrie", "Kelowna"
  ],
  "Australia": [
    "Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide",
    "Gold Coast", "Canberra", "Newcastle", "Wollongong", "Hobart",
    "Geelong", "Townsville", "Cairns", "Darwin", "Toowoomba",
    "Ballarat", "Bendigo", "Albury", "Launceston", "Mackay"
  ],
  "Germany": [
    "Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt",
    "Stuttgart", "Düsseldorf", "Dortmund", "Essen", "Leipzig",
    "Bremen", "Dresden", "Hanover", "Nuremberg", "Duisburg",
    "Bochum", "Wuppertal", "Bielefeld", "Bonn", "Münster"
  ],
  "France": [
    "Paris", "Marseille", "Lyon", "Toulouse", "Nice",
    "Nantes", "Strasbourg", "Montpellier", "Bordeaux", "Lille",
    "Rennes", "Reims", "Le Havre", "Saint-Étienne", "Toulon",
    "Grenoble", "Dijon", "Angers", "Nîmes", "Villeurbanne"
  ],
  "Japan": [
    "Tokyo", "Yokohama", "Osaka", "Nagoya", "Sapporo",
    "Fukuoka", "Kobe", "Kyoto", "Kawasaki", "Saitama",
    "Hiroshima", "Sendai", "Chiba", "Kitakyushu", "Sakai",
    "Niigata", "Hamamatsu", "Kumamoto", "Sagamihara", "Okayama"
  ],
  "China": [
    "Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Chengdu",
    "Chongqing", "Wuhan", "Tianjin", "Nanjing", "Xi\"an",
    "Hangzhou", "Zhengzhou", "Qingdao", "Dongguan", "Foshan",
    "Shenyang", "Harbin", "Jinan", "Changsha", "Kunming"
  ],
  "India": [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Ahmedabad",
    "Chennai", "Kolkata", "Surat", "Pune", "Jaipur",
    "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane",
    "Bhopal", "Visakhapatnam", "Pimpri-Chinchwad", "Patna", "Vadodara"
  ],
  "Brazil": [
    "São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Fortaleza",
    "Belo Horizonte", "Manaus", "Curitiba", "Recife", "Porto Alegre",
    "Belém", "Goiânia", "Guarulhos", "Campinas", "São Luís",
    "Maceió", "Duque de Caxias", "Natal", "Teresina", "São Bernardo do Campo"
  ],
  "Mexico": [
    "Mexico City", "Guadalajara", "Monterrey", "Puebla", "Tijuana",
    "León", "Ciudad Juárez", "Torreón", "Querétaro", "Merida",
    "Chihuahua", "San Luis Potosí", "Aguascalientes", "Hermosillo", "Saltillo",
    "Mexicali", "Culiacán", "Veracruz", "Morelia", "Reynosa"
  ],
  "Italy": [
    "Rome", "Milan", "Naples", "Turin", "Palermo",
    "Genoa", "Bologna", "Florence", "Bari", "Catania",
    "Venice", "Verona", "Messina", "Padua", "Trieste",
    "Brescia", "Taranto", "Reggio Calabria", "Modena", "Prato"
  ],
  "Spain": [
    "Madrid", "Barcelona", "Valencia", "Seville", "Zaragoza",
    "Málaga", "Murcia", "Palma", "Las Palmas", "Bilbao",
    "Alicante", "Córdoba", "Valladolid", "Vigo", "Gijón",
    "L\"Hospitalet", "Latina", "Carabanchel", "A Coruña", "Puente de Vallecas"
  ],
  "South Korea": [
    "Seoul", "Busan", "Incheon", "Daegu", "Daejeon",
    "Gwangju", "Suwon", "Ulsan", "Changwon", "Seongnam",
    "Goyang", "Yongin", "Bucheon", "Ansan", "Cheongju",
    "Jeonju", "Anyang", "Namyangju", "Hwaseong", "Pohang"
  ],
  "Saudi Arabia": [
    "Riyadh", "Jeddah", "Mecca", "Medina", "Dammam",
    "Tabuk", "Taif", "Buraydah", "Khobar", "Jubail",
    "Hofuf", "Khamis Mushait", "Hail", "Najran", "Al-Qatif",
    "Yanbu", "Abha", "Arar", "Sakaka", "Jizan"
  ],
  "United Arab Emirates": [
    "Dubai", "Abu Dhabi", "Sharjah", "Al Ain", "Ajman",
    "Ras Al Khaimah", "Fujairah", "Umm Al Quwain", "Khor Fakkan", "Dibba",
    "Jebel Ali", "Madinat Zayed", "Ruwais", "Liwa Oasis", "Hatta",
    "Dhaid", "Khalifa City", "Al Gharbia", "Al Hamra", "Al Mirfa"
  ],
  "Singapore": [
    "Singapore"
  ],
  "Malaysia": [
    "Kuala Lumpur", "George Town", "Johor Bahru", "Ipoh", "Shah Alam",
    "Petaling Jaya", "Kuching", "Kota Kinabalu", "Sandakan", "Miri",
    "Seremban", "Kuantan", "Alor Setar", "Kuala Terengganu", "Malacca",
    "Kota Bharu", "Putrajaya", "Cyberjaya", "Muar", "Batu Pahat"
  ],
  "Thailand": [
    "Bangkok", "Nonthaburi", "Nakhon Ratchasima", "Chiang Mai", "Hat Yai",
    "Udon Thani", "Pak Kret", "Khon Kaen", "Chaophraya Surasak", "Ubon Ratchathani",
    "Nakhon Si Thammarat", "Phuket", "Surat Thani", "Nakhon Pathom", "Songkhla",
    "Pathum Thani", "Chon Buri", "Si Racha", "Yala", "Samut Prakan"
  ],
  "Vietnam": [
    "Ho Chi Minh City", "Hanoi", "Da Nang", "Haiphong", "Can Tho",
    "Bien Hoa", "Nha Trang", "Hue", "Vung Tau", "Qui Nhon",
    "Rach Gia", "Long Xuyên", "Thu Dau Mot", "Thai Nguyen", "Thanh Hoa",
    "Nam Dinh", "Vinh", "My Tho", "Ha Long", "Buon Ma Thuot"
  ],
  "Philippines": [
    "Manila", "Quezon City", "Davao City", "Caloocan", "Cebu City",
    "Zamboanga City", "Taguig", "Antipolo", "Pasig", "Cagayan de Oro",
    "Parañaque", "Valenzuela", "Las Piñas", "Makati", "Bacolod",
    "General Santos", "Mandaue", "Iloilo City", "Marikina", "Pasay"
  ],
  "Indonesia": [
    "Jakarta", "Surabaya", "Bandung", "Medan", "Semarang",
    "Palembang", "Makassar", "Tangerang", "South Tangerang", "Depok",
    "Batam", "Pekanbaru", "Bogor", "Bandar Lampung", "Malang",
    "Padang", "Denpasar", "Samarinda", "Tasikmalaya", "Pontianak"
  ]
}

export default {
  countries,
  cities
}
