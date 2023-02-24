import {expressInstance, pathToEndpoints} from "../boot/config";
import express from "express";
import base from "./routes/base/base";
import match from "./routes/match/match";
import summoner from "./routes/summoner/summoner";
import swaggerJSDoc from "swagger-jsdoc";
import swaggerUi from "swagger-ui-express";

//Config
const port = 3000;
const baseUrl = "/v1";
//Swagger
const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'CNAP Backend API',
      version: 'V1.0.0',
      description: 'This is the API-Backend for the CNAP Project. The Aim of this Project is to create a Website for our' +
          ' Friend Group, providing Information on our most loved games and TableTop RPGs\n' +
          '- [CNAP Backend Repository](https://github.com/AngryBacteria/cnap-backend)\n' +
          '- [CNAP Frontend Repository](https://github.com/AngryBacteria/cnap-frontend)'
    },
  },
  apis: [pathToEndpoints], // files containing annotations as above
};
const swaggerSpec = swaggerJSDoc(options);
expressInstance.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));
//routes
expressInstance.use(express.static("public"));
expressInstance.use(baseUrl, base);
expressInstance.use(baseUrl, match);
expressInstance.use(baseUrl, summoner);
//Init
expressInstance.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});



