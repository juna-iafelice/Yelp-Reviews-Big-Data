### Final project 

from datetime import time

from pyspark.sql.functions import col, asc, concat_ws
from pyspark.sql import SparkSession
import pyspark
import re
import time
start = time.perf_counter()
# spark = SparkSession.builder.master("local[*]").appName("Yelp EDA").getOrCreate()
from pyspark.context import SparkContext
from pyspark.serializers import MarshalSerializer
# from pyspark.serializers import  PickleSerializer
sc = SparkContext("local", "serialization app", serializer = MarshalSerializer())
spark = SparkSession(sc)
spark.sparkContext.setLogLevel("ERROR")

path_from_home = "C://Users/junaz/OneDrive/Desktop/Spark/yelp/"
# reviews.parquet sample_review
user_review_path = path_from_home + "reviews.parquet"

reviews = spark.read.parquet(user_review_path)

# reviews.select(reviews.stars,reviews.text).toPandas().to_json(path_from_home+"sample_review")
business_path = path_from_home + "business.parquet"

business = spark.read.parquet(business_path)

print(reviews.show(5))

print(reviews.printSchema())

print("Counting rows and columns for reviews\n", reviews.count(), len(reviews.columns))

print(business.printSchema())

x = business.groupBy('stars').count()
print("Business stars\n", x.take(10))
used_words = open(path_from_home + 'usedWords.txt', 'r').readlines()

used_words = [x.strip() for x in used_words]


def count_words_by_star(review, star,common_words):
    review_star = review.filter(col("stars") == star)
    # review_star.show(5)
    review_star.persist(pyspark.StorageLevel.MEMORY_ONLY)
    flattened_text = review_star.select('text').rdd.flatMap(lambda t: t)

    flattened = flattened_text.filter(lambda line: len(line) > 0) \
        .flatMap(lambda line: re.split('\W+', line))

    # print(flattened.take(5))

    kv_pairs = flattened.filter(lambda word: len(word) > 0) \
        .map(lambda word: (word.lower(), 1))

    # print(kvPairs.take(5))

    countsByWord = kv_pairs.reduceByKey(lambda v1, v2: v1 + v2) \
        .sortByKey(ascending=False)

    top_words = countsByWord.map(lambda x: (x[1], x[0])) \
        .sortByKey(ascending=False)

    # print(topWords.take(10))

    filtered_words = top_words.filter(lambda w: w[1] not in common_words)
    print("Filtered words for %.0f star\n" % star, filtered_words.take(20))


stars_review = reviews.groupBy('stars')
star_rating = [1.0, 2.0, 3.0, 4.0, 5.0]
for s in star_rating:
    count_words_by_star(reviews, s,used_words)

print(spark.sparkContext._conf.getAll())
end = time.perf_counter()

print("Time taken",end-start)

spark.stop()

