$(document).ready(function () {
    var header = $('header#primary h1 a');
    var headerText = header.text();
    console.debug(headerText);
    var headerTextArray = headerText.split(' ');
    var headerTextArrayLength = headerTextArray.length;
    var lastWord = headerTextArray[headerTextArrayLength - 1];
    console.debug(lastWord);
    headerTextArray.pop();
    var firstWords = headerTextArray.join(' ');

    header.text(firstWords);
    header.append(' <span class="highlight">' + lastWord + '</span>');
});
