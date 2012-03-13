$(document).ready(function () {
    var header = $('header#primary h1 a');
    var headerText = header.text();
    console.log(headerText);
    var headerTextArray = headerText.split(' ');
    var headerTextArrayLength = headerTextArray.length;
    var lastWord = headerTextArray[headerTextArrayLength - 1];
    console.log(lastWord);
    headerTextArray.pop();
    var firstWords = headerTextArray.join(' ');

    header.text(firstWords);
    header.append(' <span class="highlight">' + lastWord + '</span>');
});
