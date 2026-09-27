Optional<String> user = Optional.empty();

// Использование штатного метода .get() без проверки
String name = user.get();   // NoSuchElementException во время исполнения!