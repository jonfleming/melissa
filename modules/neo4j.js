require("dotenv").config();
const neo4jDriver = require("neo4j-driver");
const username = process.env.neousername;
const password = process.env.neopassword;
const uri = process.env.neouri;

class neo4j {
  constructor(database) {
    this.database = database;
    this.driver = neo4jDriver.driver(
      uri,
      neo4jDriver.auth.basic(
        username,
        password
      ) /* {encrypted: 'ENCRYPTION_ON'}*/
    );
    this.session = this.driver.session({ database: database });
  }

  async runQuery(query) {
    console.log(query);
    try {
      const result = await this.session.run(query);
      const records = result.records;
      return records;
    } catch (err) {
      throw new Error(err);
    }
  }

  async runList(queries) {
    try {
      queries.forEach(async (query) => {
        console.log(query);
        const session = this.driver.session({ database: this.database });
        await session.run(query);
        await session.close();
      });
    } catch (err) {
      throw new Error(err);
    }
    this.session = this.driver.session({ database: this.database });
  }

  async close() {
    await this.session.close();
    await this.driver.close();
  }
}

module.exports = neo4j;
