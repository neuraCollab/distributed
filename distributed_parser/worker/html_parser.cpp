#include "html_parser.h"
#include <libxml/HTMLparser.h>
#include <libxml/xpath.h>
#include <iostream>

std::vector<std::string> parseHtml(const std::string &htmlContent) {
    std::vector<std::string> links;

    htmlDocPtr doc = htmlReadMemory(htmlContent.c_str(), htmlContent.size(), NULL, NULL, HTML_PARSE_NOERROR | HTML_PARSE_NOWARNING);
    if (doc == nullptr) {
        std::cerr << "Error: unable to parse HTML content" << std::endl;
        return links;
    }

    xmlXPathContextPtr xpathCtx = xmlXPathNewContext(doc);
    if (xpathCtx == nullptr) {
        std::cerr << "Error: unable to create new XPath context" << std::endl;
        xmlFreeDoc(doc);
        return links;
    }

    xmlXPathObjectPtr xpathObj = xmlXPathEvalExpression((const xmlChar *)"//a", xpathCtx);
    if (xpathObj == nullptr) {
        std::cerr << "Error: unable to evaluate XPath expression" << std::endl;
        xmlXPathFreeContext(xpathCtx);
        xmlFreeDoc(doc);
        return links;
    }

    xmlNodeSetPtr nodes = xpathObj->nodesetval;
    for (int i = 0; i < nodes->nodeNr; i++) {
        xmlNodePtr node = nodes->nodeTab[i];
        xmlChar *href = xmlGetProp(node, (const xmlChar *)"href");
        if (href != nullptr) {
            links.push_back((const char *)href);
            xmlFree(href);
        }
    }

    xmlXPathFreeObject(xpathObj);
    xmlXPathFreeContext(xpathCtx);
    xmlFreeDoc(doc);

    return links;
}
