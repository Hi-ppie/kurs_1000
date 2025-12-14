SELECT book_id, book_name, book_author ,CONVERT(SUM(copies_number), UNSIGNED) as book_number FROM book LEFT JOIN copies using(book_id)
WHERE book_id = (%s)
Group BY book_id, book_name, book_author