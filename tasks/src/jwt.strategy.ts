import { Injectable } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import { PassportStrategy } from "@nestjs/passport";
import { Strategy, ExtractJwt } from "passport-jwt";

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor(configService: ConfigService) {
    /*
    Not Yet Implemented
    const keyfile = configService.get<string>("JWT_FILE_PUBKEY");
    if (!keyfile) throw new Error("JWT_FILE_PUBKEY must be specified");
    const key = readFileSync(keyfile);
    */
    const key = "DO_NOT_USE";

    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: key,
      algorithms: ["RS256"],
    });
  }
  async validate(payload: any) {
    return { auth: "ok" };
  }
}
